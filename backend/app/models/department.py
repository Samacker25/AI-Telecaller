"""Hospital department model."""

import uuid

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base, TimestampMixin


class Department(Base, TimestampMixin):
    """A department (e.g. Cardiology) belonging to a hospital."""

    __tablename__ = "departments"
    __table_args__ = (
        UniqueConstraint("hospital_id", "name", name="uq_departments_hospital_id_name"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    hospital_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("hospitals.id", ondelete="CASCADE"), index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
