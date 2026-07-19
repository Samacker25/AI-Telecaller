"""Data access for Document metadata records."""

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document


class DocumentRepository:
    """Repository encapsulating all documents table queries."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id(self, document_id: uuid.UUID) -> Document | None:
        return await self._db.get(Document, document_id)

    async def list_filtered(self, *, status: str | None = None) -> list[Document]:
        query = select(Document).order_by(Document.created_at.desc())
        if status is not None:
            query = query.where(Document.status == status)
        result = await self._db.execute(query)
        return list(result.scalars().all())

    async def create(self, **fields: Any) -> Document:
        document = Document(**fields)
        self._db.add(document)
        await self._db.commit()
        await self._db.refresh(document)
        return document

    async def update(self, document: Document, fields: dict[str, Any]) -> Document:
        for name, value in fields.items():
            setattr(document, name, value)
        await self._db.commit()
        await self._db.refresh(document)
        return document

    async def delete(self, document: Document) -> None:
        await self._db.delete(document)
        await self._db.commit()
