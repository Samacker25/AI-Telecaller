"""User (administrator) account model."""

import enum
import uuid

from sqlalchemy import Boolean, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base, TimestampMixin


class UserRole(enum.StrEnum):
    """Roles available to dashboard users."""

    ADMIN = "admin"
    STAFF = "staff"


class User(Base, TimestampMixin):
    """Administrator / staff account for the hospital dashboard."""

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False, default=UserRole.STAFF.value)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
