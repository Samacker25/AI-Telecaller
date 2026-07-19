"""Knowledge document endpoints. Reads require auth; writes are admin-only."""

import uuid
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.embeddings import EmbeddingClient, GeminiEmbeddingClient
from app.ai.vector_store import PineconeVectorStore, VectorStore
from app.api.deps import AdminUser, CurrentUser
from app.core.config import get_settings
from app.database.session import get_db
from app.models.document import DocumentStatus
from app.schemas.document import DocumentResponse, DocumentUploadResponse
from app.services.knowledge_service import KnowledgeService

router = APIRouter(prefix="/documents", tags=["documents"])

DbSession = Annotated[AsyncSession, Depends(get_db)]


def get_knowledge_service(db: DbSession) -> KnowledgeService:
    """Build the knowledge service with providers from configuration.

    Providers are optional so the API stays usable in environments without
    AI credentials; ingestion then records a ``failed`` status instead.
    """
    settings = get_settings()
    embedder: EmbeddingClient | None = None
    vector_store: VectorStore | None = None
    if settings.gemini_api_key:
        embedder = GeminiEmbeddingClient(
            api_key=settings.gemini_api_key,
            model=settings.embedding_model,
            dimension=settings.embedding_dimension,
        )
    if settings.pinecone_api_key and settings.pinecone_index:
        vector_store = PineconeVectorStore(
            api_key=settings.pinecone_api_key, index_name=settings.pinecone_index
        )
    return KnowledgeService(
        db,
        embedder=embedder,
        vector_store=vector_store,
        upload_dir=Path(settings.upload_directory),
    )


Knowledge = Annotated[KnowledgeService, Depends(get_knowledge_service)]


@router.post("", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: Annotated[UploadFile, File()],
    admin: AdminUser,
    service: Knowledge,
) -> DocumentUploadResponse:
    """Upload a knowledge document (PDF, DOCX, or TXT) and index it. Admin only."""
    content = await file.read()
    document = await service.upload_document(
        file_name=file.filename or "",
        content=content,
        uploaded_by=admin.id,
    )
    return DocumentUploadResponse(document_id=document.id, status=DocumentStatus(document.status))


@router.get("", response_model=list[DocumentResponse])
async def list_documents(
    user: CurrentUser,
    service: Knowledge,
    status_filter: Annotated[DocumentStatus | None, Query(alias="status")] = None,
) -> list[DocumentResponse]:
    """List uploaded documents, optionally filtered by status. Authenticated."""
    documents = await service.list_documents(status_filter=status_filter)
    return [DocumentResponse.model_validate(document) for document in documents]


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: uuid.UUID, user: CurrentUser, service: Knowledge
) -> DocumentResponse:
    """Return a document's metadata and ingestion status. Authenticated."""
    document = await service.get_document(document_id)
    return DocumentResponse.model_validate(document)


@router.post("/{document_id}/reindex", response_model=DocumentResponse)
async def reindex_document(
    document_id: uuid.UUID, admin: AdminUser, service: Knowledge
) -> DocumentResponse:
    """Re-run the ingestion pipeline for a document. Admin only."""
    document = await service.reindex_document(document_id)
    return DocumentResponse.model_validate(document)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(document_id: uuid.UUID, admin: AdminUser, service: Knowledge) -> None:
    """Delete a document, its stored file, and its embeddings. Admin only."""
    await service.delete_document(document_id)
