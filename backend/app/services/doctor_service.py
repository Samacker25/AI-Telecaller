"""Doctor business logic: CRUD with department validation and OPD schedules."""

import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.core.logging import get_logger
from app.models.doctor import Doctor
from app.repositories.doctor_repository import DoctorRepository
from app.schemas.doctor import DoctorCreate, DoctorUpdate
from app.services.department_service import DepartmentService

logger = get_logger("app.services.doctor")


class DoctorService:
    """Manages doctors and their OPD working hours."""

    def __init__(self, db: AsyncSession) -> None:
        self._doctors = DoctorRepository(db)
        self._department_service = DepartmentService(db)

    async def list_doctors(
        self,
        *,
        department_id: uuid.UUID | None = None,
        specialization: str | None = None,
        available: bool | None = None,
    ) -> list[Doctor]:
        return await self._doctors.list_filtered(
            department_id=department_id,
            specialization=specialization,
            available=available,
        )

    async def get_doctor(self, doctor_id: uuid.UUID) -> Doctor:
        doctor = await self._doctors.get_by_id(doctor_id)
        if doctor is None:
            raise NotFoundError(code="DOCTOR_NOT_FOUND", message="Doctor not found.")
        return doctor

    async def create_doctor(self, payload: DoctorCreate) -> Doctor:
        department = await self._department_service.get_department(payload.department_id)
        fields = payload.model_dump()
        fields["opd_schedule"] = self._dump_schedule(payload)
        doctor = await self._doctors.create(hospital_id=department.hospital_id, **fields)
        logger.info(
            "doctor created",
            extra={"extra_fields": {"doctor_id": str(doctor.id)}},
        )
        return doctor

    async def update_doctor(self, doctor_id: uuid.UUID, payload: DoctorUpdate) -> Doctor:
        doctor = await self.get_doctor(doctor_id)
        fields = payload.model_dump(exclude_unset=True)
        if "department_id" in fields:
            department = await self._department_service.get_department(payload.department_id)
            fields["hospital_id"] = department.hospital_id
        if "opd_schedule" in fields:
            fields["opd_schedule"] = self._dump_schedule(payload)
        doctor = await self._doctors.update(doctor, fields)
        logger.info(
            "doctor updated",
            extra={"extra_fields": {"doctor_id": str(doctor.id), "fields": list(fields)}},
        )
        return doctor

    async def delete_doctor(self, doctor_id: uuid.UUID) -> None:
        doctor = await self.get_doctor(doctor_id)
        await self._doctors.delete(doctor)
        logger.info(
            "doctor deleted",
            extra={"extra_fields": {"doctor_id": str(doctor_id)}},
        )

    @staticmethod
    def _dump_schedule(payload: DoctorCreate | DoctorUpdate) -> dict[str, Any] | None:
        """Serialize the validated OPD schedule to JSON-safe data for storage."""
        if payload.opd_schedule is None:
            return None
        return payload.opd_schedule.model_dump(mode="json")
