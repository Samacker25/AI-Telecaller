"""ORM models.

Import every model here so Alembic autogenerate can discover it.
"""

from app.database.base import Base
from app.models.department import Department
from app.models.doctor import Doctor
from app.models.hospital import Hospital
from app.models.user import User, UserRole

__all__ = ["Base", "Department", "Doctor", "Hospital", "User", "UserRole"]
