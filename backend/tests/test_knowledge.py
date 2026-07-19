"""API tests for knowledge document upload, ingestion lifecycle, and CRUD.

The embedding client and vector store are replaced with in-memory fakes,
so no external AI services are required.
"""

import uuid
from pathlib import Path
from typing import Annotated

import pytest
from fastapi import Depends
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.chunker import Chunk
from app.api.v1.documents import get_knowledge_service
from app.database.session import get_db
from app.services.knowledge_service import KnowledgeService


class FakeEmbedder:
    """Deterministic embeddings without network access."""

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [[1.0, float(len(text))] for text in texts]


class FakeVectorStore:
    """Records upserted vectors in memory, keyed like Pinecone IDs."""

    def __init__(self) -> None:
        self.vectors: dict[str, dict] = {}
        self.upsert_calls = 0

    def upsert_chunks(
        self,
        *,
        hospital_id: uuid.UUID,
        document_id: uuid.UUID,
        file_name: str,
        chunks: list[Chunk],
        vectors: list[list[float]],
    ) -> None:
        self.upsert_calls += 1
        for chunk, vector in zip(chunks, vectors, strict=True):
            self.vectors[f"{document_id}:{chunk.index}"] = {
                "values": vector,
                "metadata": {
                    "document_id": str(document_id),
                    "hospital_id": str(hospital_id),
                    "file_name": file_name,
                    "text": chunk.text,
                },
            }

    def delete_document(self, *, hospital_id: uuid.UUID, document_id: uuid.UUID) -> None:
        prefix = f"{document_id}:"
        for key in [key for key in self.vectors if key.startswith(prefix)]:
            del self.vectors[key]


@pytest.fixture
def vector_store() -> FakeVectorStore:
    return FakeVectorStore()


@pytest.fixture
def upload_dir(tmp_path: Path) -> Path:
    return tmp_path / "uploads"


@pytest.fixture
def knowledge_app(app, vector_store: FakeVectorStore, upload_dir: Path):
    """App with the knowledge service wired to fakes and a temp upload dir."""

    def override(db: Annotated[AsyncSession, Depends(get_db)]) -> KnowledgeService:
        return KnowledgeService(
            db, embedder=FakeEmbedder(), vector_store=vector_store, upload_dir=upload_dir
        )

    app.dependency_overrides[get_knowledge_service] = override
    return app


async def upload_txt(
    client: AsyncClient,
    headers: dict[str, str],
    *,
    name: str = "faq.txt",
    content: bytes = b"Visiting hours are 9 AM to 5 PM.\n\nThe emergency ward is open 24 hours.",
):
    return await client.post(
        "/api/v1/documents",
        files={"file": (name, content, "text/plain")},
        headers=headers,
    )


class TestUploadDocument:
    async def test_upload_and_index_txt(
        self, knowledge_app, client, admin_headers, hospital, vector_store, upload_dir
    ):
        response = await upload_txt(client, admin_headers)
        assert response.status_code == 201, response.text
        body = response.json()
        assert body["status"] == "indexed"

        detail = await client.get(f"/api/v1/documents/{body['document_id']}", headers=admin_headers)
        assert detail.status_code == 200
        document = detail.json()
        assert document["file_name"] == "faq.txt"
        assert document["file_type"] == "txt"
        assert document["chunk_count"] >= 1
        assert document["error_message"] is None

        stored = list(upload_dir.glob("*.txt"))
        assert len(stored) == 1
        assert vector_store.vectors, "chunks should be upserted to the vector store"
        first = next(iter(vector_store.vectors.values()))
        assert first["metadata"]["hospital_id"] == hospital["id"]
        assert "Visiting hours" in first["metadata"]["text"]

    async def test_upload_without_hospital_profile(self, knowledge_app, client, admin_headers):
        response = await upload_txt(client, admin_headers)
        assert response.status_code == 404
        assert response.json()["error"]["code"] == "HOSPITAL_NOT_CONFIGURED"

    async def test_unsupported_file_type_rejected(
        self, knowledge_app, client, admin_headers, hospital
    ):
        response = await upload_txt(client, admin_headers, name="malware.exe")
        assert response.status_code == 400
        assert response.json()["error"]["code"] == "UNSUPPORTED_FILE_TYPE"

    async def test_empty_file_rejected(self, knowledge_app, client, admin_headers, hospital):
        response = await upload_txt(client, admin_headers, content=b"")
        assert response.status_code == 400
        assert response.json()["error"]["code"] == "EMPTY_FILE"

    async def test_oversized_file_rejected(self, knowledge_app, client, admin_headers, hospital):
        oversized = b"a" * (10 * 1024 * 1024 + 1)
        response = await upload_txt(client, admin_headers, content=oversized)
        assert response.status_code == 413
        assert response.json()["error"]["code"] == "FILE_TOO_LARGE"

    async def test_staff_cannot_upload(self, knowledge_app, client, staff_headers, hospital):
        response = await upload_txt(client, staff_headers)
        assert response.status_code == 403

    async def test_corrupt_file_marked_failed(
        self, knowledge_app, client, admin_headers, hospital, vector_store
    ):
        response = await upload_txt(client, admin_headers, name="broken.pdf", content=b"not a pdf")
        assert response.status_code == 201
        body = response.json()
        assert body["status"] == "failed"

        detail = await client.get(f"/api/v1/documents/{body['document_id']}", headers=admin_headers)
        assert detail.json()["error_message"]
        assert not vector_store.vectors

    async def test_unconfigured_providers_marked_failed(
        self, app, client, admin_headers, hospital, upload_dir
    ):
        def override(db: Annotated[AsyncSession, Depends(get_db)]) -> KnowledgeService:
            return KnowledgeService(db, upload_dir=upload_dir)

        app.dependency_overrides[get_knowledge_service] = override
        response = await upload_txt(client, admin_headers)
        assert response.status_code == 201
        assert response.json()["status"] == "failed"


class TestListAndGetDocuments:
    async def test_list_requires_auth(self, knowledge_app, client):
        response = await client.get("/api/v1/documents")
        assert response.status_code == 401

    async def test_list_and_filter_by_status(
        self, knowledge_app, client, admin_headers, staff_headers, hospital
    ):
        await upload_txt(client, admin_headers, name="a.txt")
        await upload_txt(client, admin_headers, name="broken.pdf", content=b"not a pdf")

        response = await client.get("/api/v1/documents", headers=staff_headers)
        assert response.status_code == 200
        assert len(response.json()) == 2

        response = await client.get("/api/v1/documents?status=indexed", headers=staff_headers)
        names = [document["file_name"] for document in response.json()]
        assert names == ["a.txt"]

    async def test_get_missing_document(self, knowledge_app, client, admin_headers):
        response = await client.get(f"/api/v1/documents/{uuid.uuid4()}", headers=admin_headers)
        assert response.status_code == 404
        assert response.json()["error"]["code"] == "DOCUMENT_NOT_FOUND"


class TestReindexDocument:
    async def test_reindex_replaces_vectors(
        self, knowledge_app, client, admin_headers, hospital, vector_store
    ):
        uploaded = (await upload_txt(client, admin_headers)).json()
        document_id = uploaded["document_id"]

        response = await client.post(
            f"/api/v1/documents/{document_id}/reindex", headers=admin_headers
        )
        assert response.status_code == 200, response.text
        assert response.json()["status"] == "indexed"
        assert vector_store.upsert_calls == 2

    async def test_reindex_requires_admin(
        self, knowledge_app, client, admin_headers, staff_headers, hospital
    ):
        uploaded = (await upload_txt(client, admin_headers)).json()
        response = await client.post(
            f"/api/v1/documents/{uploaded['document_id']}/reindex", headers=staff_headers
        )
        assert response.status_code == 403


class TestDeleteDocument:
    async def test_delete_removes_vectors_file_and_record(
        self, knowledge_app, client, admin_headers, hospital, vector_store, upload_dir
    ):
        uploaded = (await upload_txt(client, admin_headers)).json()
        document_id = uploaded["document_id"]
        assert vector_store.vectors

        response = await client.delete(f"/api/v1/documents/{document_id}", headers=admin_headers)
        assert response.status_code == 204
        assert not vector_store.vectors
        assert not list(upload_dir.glob("*"))

        response = await client.get(f"/api/v1/documents/{document_id}", headers=admin_headers)
        assert response.status_code == 404

    async def test_delete_requires_admin(
        self, knowledge_app, client, admin_headers, staff_headers, hospital
    ):
        uploaded = (await upload_txt(client, admin_headers)).json()
        response = await client.delete(
            f"/api/v1/documents/{uploaded['document_id']}", headers=staff_headers
        )
        assert response.status_code == 403
