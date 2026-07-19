"""Knowledge document metadata model.

PostgreSQL stores only document metadata; the extracted text is chunked,
embedded, and stored in the vector database (Pinecone).
"""

import enum
import uuid

from sqlalchemy import ForeignKey, Integer, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base, TimestampMixin


class DocumentStatus(enum.StrEnum):
    """Lifecycle of an uploaded knowledge document."""

    UPLOADED = "uploaded"
    PROCESSING = "processing"
    INDEXED = "indexed"
    FAILED = "failed"


class DocumentType(enum.StrEnum):
    """Supported knowledge document file types."""

    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"


class Document(Base, TimestampMixin):
    """Metadata for an uploaded knowledge document."""

    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    hospital_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("hospitals.id", ondelete="CASCADE"), index=True, nullable=False
    )
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(10), nullable=False)
    storage_path: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), index=True, nullable=False, default=DocumentStatus.UPLOADED.value
    )
    chunk_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error_message: Mapped[str | None] = mapped_column(Text)
    uploaded_by: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="SET NULL")
    )
