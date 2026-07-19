"""Data access for Doctor records."""

import uuid
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.doctor import Doctor


class DoctorRepository:
    """Repository encapsulating all doctor table queries."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id(self, doctor_id: uuid.UUID) -> Doctor | None:
        return await self._db.get(Doctor, doctor_id)

    async def list_filtered(
        self,
        *,
        department_id: uuid.UUID | None = None,
        specialization: str | None = None,
        available: bool | None = None,
    ) -> list[Doctor]:
        query = select(Doctor).order_by(Doctor.name)
        if department_id is not None:
            query = query.where(Doctor.department_id == department_id)
        if specialization is not None:
            query = query.where(func.lower(Doctor.specialization) == specialization.lower())
        if available is not None:
            query = query.where(Doctor.is_available == available)
        result = await self._db.execute(query)
        return list(result.scalars().all())

    async def count_by_department(self, department_id: uuid.UUID) -> int:
        result = await self._db.execute(
            select(func.count()).select_from(Doctor).where(Doctor.department_id == department_id)
        )
        return result.scalar_one()

    async def create(self, **fields: Any) -> Doctor:
        doctor = Doctor(**fields)
        self._db.add(doctor)
        await self._db.commit()
        await self._db.refresh(doctor)
        return doctor

    async def update(self, doctor: Doctor, fields: dict[str, Any]) -> Doctor:
        for name, value in fields.items():
            setattr(doctor, name, value)
        await self._db.commit()
        await self._db.refresh(doctor)
        return doctor

    async def delete(self, doctor: Doctor) -> None:
        await self._db.delete(doctor)
        await self._db.commit()
