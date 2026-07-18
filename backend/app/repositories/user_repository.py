"""Data access for User records."""

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:
    """Repository encapsulating all user table queries."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        return await self._db.get(User, user_id)

    async def get_by_email(self, email: str) -> User | None:
        result = await self._db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def list_all(self) -> list[User]:
        result = await self._db.execute(select(User).order_by(User.created_at))
        return list(result.scalars().all())

    async def count(self) -> int:
        result = await self._db.execute(select(func.count()).select_from(User))
        return result.scalar_one()

    async def create(self, *, name: str, email: str, password_hash: str, role: str) -> User:
        user = User(name=name, email=email, password_hash=password_hash, role=role)
        self._db.add(user)
        await self._db.commit()
        await self._db.refresh(user)
        return user
