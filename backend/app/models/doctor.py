"""Doctor model."""

import uuid
from typing import Any

from sqlalchemy import Boolean, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base, JSONColumn, TimestampMixin


class Doctor(Base, TimestampMixin):
    """A doctor attached to a hospital department.

    ``opd_schedule`` stores validated weekly working hours as JSON
    (see ``app.schemas.schedule.WeeklySchedule``).
    """

    __tablename__ = "doctors"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    hospital_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("hospitals.id", ondelete="CASCADE"), index=True, nullable=False
    )
    department_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("departments.id", ondelete="RESTRICT"), index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    specialization: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    qualification: Mapped[str | None] = mapped_column(String(255))
    opd_schedule: Mapped[dict[str, Any] | None] = mapped_column(JSONColumn)
    is_available: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
