"""Data access for Hospital records."""

import uuid
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.hospital import Hospital


class HospitalRepository:
    """Repository encapsulating all hospital table queries."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id(self, hospital_id: uuid.UUID) -> Hospital | None:
        return await self._db.get(Hospital, hospital_id)

    async def get_first(self) -> Hospital | None:
        """Return the single MVP hospital (oldest record), if configured."""
        result = await self._db.execute(select(Hospital).order_by(Hospital.created_at).limit(1))
        return result.scalar_one_or_none()

    async def list_all(self) -> list[Hospital]:
        result = await self._db.execute(select(Hospital).order_by(Hospital.created_at))
        return list(result.scalars().all())

    async def count(self) -> int:
        result = await self._db.execute(select(func.count()).select_from(Hospital))
        return result.scalar_one()

    async def create(self, **fields: Any) -> Hospital:
        hospital = Hospital(**fields)
        self._db.add(hospital)
        await self._db.commit()
        await self._db.refresh(hospital)
        return hospital

    async def update(self, hospital: Hospital, fields: dict[str, Any]) -> Hospital:
        for name, value in fields.items():
            setattr(hospital, name, value)
        await self._db.commit()
        await self._db.refresh(hospital)
        return hospital
