"""Knowledge base business logic: document upload, ingestion, and CRUD.

Ingestion pipeline: parse -> clean -> chunk -> embed -> index (Pinecone).
PostgreSQL keeps only metadata; extracted text lives in the vector store.
"""

import uuid
from pathlib import Path

from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from app.ai.chunker import chunk_text
from app.ai.embeddings import EmbeddingClient, EmbeddingError
from app.ai.parsers import DocumentParseError, extract_text
from app.ai.text_cleaner import clean_text
from app.ai.vector_store import VectorStore, VectorStoreError
from app.core.config import get_settings
from app.core.exceptions import AppError, NotFoundError, ServiceUnavailableError
from app.core.logging import get_logger
from app.models.document import Document, DocumentStatus, DocumentType
from app.repositories.document_repository import DocumentRepository
from app.services.hospital_service import HospitalService

logger = get_logger("app.services.knowledge")


class KnowledgeService:
    """Manages knowledge documents and their vector-store lifecycle."""

    def __init__(
        self,
        db: AsyncSession,
        *,
        embedder: EmbeddingClient | None = None,
        vector_store: VectorStore | None = None,
        upload_dir: Path | None = None,
    ) -> None:
        settings = get_settings()
        self._documents = DocumentRepository(db)
        self._hospital_service = HospitalService(db)
        self._embedder = embedder
        self._vector_store = vector_store
        self._upload_dir = upload_dir or Path(settings.upload_directory)
        self._max_upload_size = settings.max_upload_size
        self._chunk_size = settings.chunk_size
        self._chunk_overlap = settings.chunk_overlap

    async def list_documents(
        self, *, status_filter: DocumentStatus | None = None
    ) -> list[Document]:
        status_value = status_filter.value if status_filter else None
        return await self._documents.list_filtered(status=status_value)

    async def get_document(self, document_id: uuid.UUID) -> Document:
        document = await self._documents.get_by_id(document_id)
        if document is None:
            raise NotFoundError(code="DOCUMENT_NOT_FOUND", message="Document not found.")
        return document

    async def upload_document(
        self, *, file_name: str, content: bytes, uploaded_by: uuid.UUID
    ) -> Document:
        """Validate, store, and index an uploaded knowledge document.

        The document is always persisted; ingestion failures are recorded on
        the record (status ``failed``) instead of failing the upload.
        """
        file_type = self._validate_upload(file_name=file_name, content=content)
        hospital = await self._hospital_service.get_default_hospital()

        document = await self._documents.create(
            hospital_id=hospital.id,
            file_name=Path(file_name).name[:255],
            file_type=file_type.value,
            storage_path="",
            status=DocumentStatus.UPLOADED.value,
            uploaded_by=uploaded_by,
        )
        storage_path = await run_in_threadpool(self._store_file, document.id, file_type, content)
        document = await self._documents.update(document, {"storage_path": str(storage_path)})
        logger.info(
            "document uploaded",
            extra={"extra_fields": {"document_id": str(document.id), "type": file_type.value}},
        )
        return await self._process(document)

    async def reindex_document(self, document_id: uuid.UUID) -> Document:
        """Re-run the ingestion pipeline for an existing document."""
        document = await self.get_document(document_id)
        if not Path(document.storage_path).is_file():
            raise ServiceUnavailableError(
                code="DOCUMENT_FILE_MISSING",
                message="Stored document file is missing. Upload the document again.",
            )
        return await self._process(document)

    async def delete_document(self, document_id: uuid.UUID) -> None:
        """Remove a document's vectors, stored file, and metadata record."""
        document = await self.get_document(document_id)
        if self._vector_store is not None:
            try:
                await run_in_threadpool(
                    self._vector_store.delete_document,
                    hospital_id=document.hospital_id,
                    document_id=document.id,
                )
            except VectorStoreError as exc:
                raise ServiceUnavailableError(
                    code="VECTOR_STORE_UNAVAILABLE",
                    message="Could not remove document embeddings. Try again later.",
                ) from exc
        await run_in_threadpool(self._remove_file, document.storage_path)
        await self._documents.delete(document)
        logger.info(
            "document deleted",
            extra={"extra_fields": {"document_id": str(document_id)}},
        )

    async def _process(self, document: Document) -> Document:
        """Run parse -> clean -> chunk -> embed -> index, tracking status."""
        document = await self._documents.update(
            document, {"status": DocumentStatus.PROCESSING.value, "error_message": None}
        )
        try:
            chunk_total = await self._ingest(document)
        except Exception as exc:
            safe_message = self._safe_failure_message(exc)
            logger.warning(
                "document ingestion failed",
                extra={
                    "extra_fields": {
                        "document_id": str(document.id),
                        "error": type(exc).__name__,
                    }
                },
            )
            return await self._documents.update(
                document,
                {"status": DocumentStatus.FAILED.value, "error_message": safe_message},
            )

        document = await self._documents.update(
            document,
            {"status": DocumentStatus.INDEXED.value, "chunk_count": chunk_total},
        )
        logger.info(
            "document indexed",
            extra={"extra_fields": {"document_id": str(document.id), "chunks": chunk_total}},
        )
        return document

    async def _ingest(self, document: Document) -> int:
        """Extract, chunk, embed, and index the document. Returns the chunk count."""
        if self._embedder is None or self._vector_store is None:
            raise ServiceUnavailableError(
                code="AI_NOT_CONFIGURED",
                message="Embedding or vector store provider is not configured.",
            )

        file_type = DocumentType(document.file_type)
        raw_text = await run_in_threadpool(extract_text, Path(document.storage_path), file_type)
        chunks = chunk_text(
            clean_text(raw_text),
            chunk_size=self._chunk_size,
            chunk_overlap=self._chunk_overlap,
        )
        if not chunks:
            raise DocumentParseError("Document contains no indexable content.")

        vectors = await run_in_threadpool(
            self._embedder.embed_texts, [chunk.text for chunk in chunks]
        )
        # Replace any previously indexed vectors before writing the new set.
        await run_in_threadpool(
            self._vector_store.delete_document,
            hospital_id=document.hospital_id,
            document_id=document.id,
        )
        await run_in_threadpool(
            self._vector_store.upsert_chunks,
            hospital_id=document.hospital_id,
            document_id=document.id,
            file_name=document.file_name,
            chunks=chunks,
            vectors=vectors,
        )
        return len(chunks)

    def _validate_upload(self, *, file_name: str, content: bytes) -> DocumentType:
        """Check file type and size before accepting an upload."""
        suffix = Path(file_name).suffix.lower().lstrip(".")
        try:
            file_type = DocumentType(suffix)
        except ValueError:
            raise AppError(
                code="UNSUPPORTED_FILE_TYPE",
                message="Only PDF, DOCX, and TXT files are supported.",
                status_code=status.HTTP_400_BAD_REQUEST,
            ) from None
        if not content:
            raise AppError(
                code="EMPTY_FILE",
                message="Uploaded file is empty.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        if len(content) > self._max_upload_size:
            raise AppError(
                code="FILE_TOO_LARGE",
                message=f"File exceeds the maximum size of {self._max_upload_size} bytes.",
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            )
        return file_type

    def _store_file(self, document_id: uuid.UUID, file_type: DocumentType, content: bytes) -> Path:
        """Write upload bytes to disk under a server-generated file name."""
        self._upload_dir.mkdir(parents=True, exist_ok=True)
        path = self._upload_dir / f"{document_id}.{file_type.value}"
        path.write_bytes(content)
        return path

    @staticmethod
    def _remove_file(storage_path: str) -> None:
        if storage_path:
            Path(storage_path).unlink(missing_ok=True)

    @staticmethod
    def _safe_failure_message(exc: Exception) -> str:
        """Map ingestion errors to messages safe to store and show to admins."""
        if isinstance(exc, DocumentParseError | EmbeddingError):
            return str(exc)
        if isinstance(exc, AppError):
            return exc.message
        if isinstance(exc, VectorStoreError):
            return "Vector store indexing failed."
        return "Document processing failed."
