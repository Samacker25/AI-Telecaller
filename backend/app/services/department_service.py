"""Department business logic: CRUD with duplicate-name and delete protection."""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError
from app.core.logging import get_logger
from app.models.department import Department
from app.repositories.department_repository import DepartmentRepository
from app.repositories.doctor_repository import DoctorRepository
from app.schemas.department import DepartmentCreate, DepartmentUpdate
from app.services.hospital_service import HospitalService

logger = get_logger("app.services.department")


class DepartmentService:
    """Manages hospital departments."""

    def __init__(self, db: AsyncSession) -> None:
        self._departments = DepartmentRepository(db)
        self._doctors = DoctorRepository(db)
        self._hospital_service = HospitalService(db)

    async def list_departments(self) -> list[Department]:
        return await self._departments.list_all()

    async def get_department(self, department_id: uuid.UUID) -> Department:
        department = await self._departments.get_by_id(department_id)
        if department is None:
            raise NotFoundError(code="DEPARTMENT_NOT_FOUND", message="Department not found.")
        return department

    async def create_department(self, payload: DepartmentCreate) -> Department:
        hospital = await self._hospital_service.get_default_hospital()
        await self._ensure_name_available(hospital.id, payload.name)
        department = await self._departments.create(hospital_id=hospital.id, **payload.model_dump())
        logger.info(
            "department created",
            extra={"extra_fields": {"department_id": str(department.id)}},
        )
        return department

    async def update_department(
        self, department_id: uuid.UUID, payload: DepartmentUpdate
    ) -> Department:
        department = await self.get_department(department_id)
        fields = payload.model_dump(exclude_unset=True)
        new_name = fields.get("name")
        if new_name is not None and new_name.lower() != department.name.lower():
            await self._ensure_name_available(department.hospital_id, new_name)
        department = await self._departments.update(department, fields)
        logger.info(
            "department updated",
            extra={"extra_fields": {"department_id": str(department.id), "fields": list(fields)}},
        )
        return department

    async def delete_department(self, department_id: uuid.UUID) -> None:
        department = await self.get_department(department_id)
        if await self._doctors.count_by_department(department.id) > 0:
            raise ConflictError(
                code="DEPARTMENT_HAS_DOCTORS",
                message="Reassign or delete this department's doctors first.",
            )
        await self._departments.delete(department)
        logger.info(
            "department deleted",
            extra={"extra_fields": {"department_id": str(department_id)}},
        )

    async def _ensure_name_available(self, hospital_id: uuid.UUID, name: str) -> None:
        if await self._departments.get_by_name(hospital_id, name) is not None:
            raise ConflictError(
                code="DEPARTMENT_ALREADY_EXISTS",
                message="A department with this name already exists.",
            )
