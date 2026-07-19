"""Data access for Department records."""

import uuid
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.department import Department


class DepartmentRepository:
    """Repository encapsulating all department table queries."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id(self, department_id: uuid.UUID) -> Department | None:
        return await self._db.get(Department, department_id)

    async def get_by_name(self, hospital_id: uuid.UUID, name: str) -> Department | None:
        result = await self._db.execute(
            select(Department).where(
                Department.hospital_id == hospital_id,
                func.lower(Department.name) == name.lower(),
            )
        )
        return result.scalar_one_or_none()

    async def list_all(self) -> list[Department]:
        result = await self._db.execute(select(Department).order_by(Department.name))
        return list(result.scalars().all())

    async def create(self, **fields: Any) -> Department:
        department = Department(**fields)
        self._db.add(department)
        await self._db.commit()
        await self._db.refresh(department)
        return department

    async def update(self, department: Department, fields: dict[str, Any]) -> Department:
        for name, value in fields.items():
            setattr(department, name, value)
        await self._db.commit()
        await self._db.refresh(department)
        return department

    async def delete(self, department: Department) -> None:
        await self._db.delete(department)
        await self._db.commit()
