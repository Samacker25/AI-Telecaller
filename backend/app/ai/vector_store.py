"""Vector storage for knowledge chunks.

Pinecone stores only embeddings and retrieval metadata; all operational
data stays in PostgreSQL. Vector IDs use the form ``{document_id}:{chunk_index}``
and each hospital gets its own namespace (future multi-tenancy).
"""

import uuid
from dataclasses import dataclass
from typing import Any, Protocol

from app.ai.chunker import Chunk
from app.core.logging import get_logger

logger = get_logger("app.ai.vector_store")

_UPSERT_BATCH_SIZE = 100


class VectorStoreError(Exception):
    """Raised when the vector database operation fails."""


@dataclass(frozen=True)
class RetrievedChunk:
    """A knowledge chunk returned by similarity search."""

    document_id: str
    chunk_index: int
    file_name: str
    text: str
    score: float


class VectorStore(Protocol):
    """Stores, searches, and removes embedded document chunks."""

    def upsert_chunks(
        self,
        *,
        hospital_id: uuid.UUID,
        document_id: uuid.UUID,
        file_name: str,
        chunks: list[Chunk],
        vectors: list[list[float]],
    ) -> None: ...

    def query(
        self, *, hospital_id: uuid.UUID, vector: list[float], top_k: int
    ) -> list[RetrievedChunk]: ...

    def delete_document(self, *, hospital_id: uuid.UUID, document_id: uuid.UUID) -> None: ...


class PineconeVectorStore:
    """Production vector store backed by a Pinecone index."""

    def __init__(self, api_key: str, index_name: str) -> None:
        from pinecone import Pinecone

        self._index = Pinecone(api_key=api_key).Index(index_name)

    def upsert_chunks(
        self,
        *,
        hospital_id: uuid.UUID,
        document_id: uuid.UUID,
        file_name: str,
        chunks: list[Chunk],
        vectors: list[list[float]],
    ) -> None:
        records: list[dict[str, Any]] = [
            {
                "id": f"{document_id}:{chunk.index}",
                "values": vector,
                "metadata": {
                    "document_id": str(document_id),
                    "hospital_id": str(hospital_id),
                    "chunk_index": chunk.index,
                    "file_name": file_name,
                    "text": chunk.text,
                },
            }
            for chunk, vector in zip(chunks, vectors, strict=True)
        ]
        try:
            for start in range(0, len(records), _UPSERT_BATCH_SIZE):
                batch = records[start : start + _UPSERT_BATCH_SIZE]
                self._index.upsert(vectors=batch, namespace=str(hospital_id))
        except Exception as exc:
            logger.warning(
                "vector upsert failed",
                extra={"extra_fields": {"document_id": str(document_id)}},
            )
            raise VectorStoreError("Vector store upsert failed.") from exc

    def query(
        self, *, hospital_id: uuid.UUID, vector: list[float], top_k: int
    ) -> list[RetrievedChunk]:
        try:
            response = self._index.query(
                vector=vector,
                top_k=top_k,
                namespace=str(hospital_id),
                include_metadata=True,
            )
        except Exception as exc:
            logger.warning(
                "vector query failed",
                extra={"extra_fields": {"hospital_id": str(hospital_id)}},
            )
            raise VectorStoreError("Vector store query failed.") from exc

        results: list[RetrievedChunk] = []
        for match in response.matches:
            metadata = match.metadata or {}
            results.append(
                RetrievedChunk(
                    document_id=str(metadata.get("document_id", "")),
                    chunk_index=int(metadata.get("chunk_index", 0)),
                    file_name=str(metadata.get("file_name", "")),
                    text=str(metadata.get("text", "")),
                    score=float(match.score or 0.0),
                )
            )
        return results

    def delete_document(self, *, hospital_id: uuid.UUID, document_id: uuid.UUID) -> None:
        namespace = str(hospital_id)
        try:
            # Serverless indexes do not support metadata-filter deletes,
            # so delete by listing IDs with the document prefix.
            for id_batch in self._index.list(prefix=f"{document_id}:", namespace=namespace):
                if id_batch:
                    self._index.delete(ids=list(id_batch), namespace=namespace)
        except Exception as exc:
            logger.warning(
                "vector delete failed",
                extra={"extra_fields": {"document_id": str(document_id)}},
            )
            raise VectorStoreError("Vector store delete failed.") from exc
