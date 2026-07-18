"""ORM models.

Import every model here so Alembic autogenerate can discover it.
"""

from app.database.base import Base
from app.models.user import User, UserRole

__all__ = ["Base", "User", "UserRole"]
