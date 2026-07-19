"""Hospital profile model."""

import uuid
from typing import Any

from sqlalchemy import String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base, JSONColumn, TimestampMixin


class Hospital(Base, TimestampMixin):
    """Hospital profile. The MVP supports a single hospital; the schema is
    multi-hospital ready for the future SaaS phase."""

    __tablename__ = "hospitals"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[str | None] = mapped_column(Text)
    phone: Mapped[str | None] = mapped_column(String(50))
    email: Mapped[str | None] = mapped_column(String(320))
    website: Mapped[str | None] = mapped_column(String(500))
    settings: Mapped[dict[str, Any] | None] = mapped_column(JSONColumn)
