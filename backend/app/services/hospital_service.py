"""Hospital business logic: profile CRUD and hospital settings."""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError
from app.core.logging import get_logger
from app.models.hospital import Hospital
from app.repositories.hospital_repository import HospitalRepository
from app.schemas.hospital import HospitalCreate, HospitalSettings, HospitalUpdate

logger = get_logger("app.services.hospital")


class HospitalService:
    """Manages the hospital profile and its operational settings."""

    def __init__(self, db: AsyncSession) -> None:
        self._hospitals = HospitalRepository(db)

    async def create_hospital(self, payload: HospitalCreate) -> Hospital:
        """Create the hospital profile. The MVP supports exactly one hospital."""
        if await self._hospitals.count() > 0:
            raise ConflictError(
                code="HOSPITAL_ALREADY_EXISTS",
                message="A hospital profile already exists. Update it instead.",
            )
        hospital = await self._hospitals.create(**payload.model_dump())
        logger.info(
            "hospital created",
            extra={"extra_fields": {"hospital_id": str(hospital.id)}},
        )
        return hospital

    async def list_hospitals(self) -> list[Hospital]:
        return await self._hospitals.list_all()

    async def get_hospital(self, hospital_id: uuid.UUID) -> Hospital:
        hospital = await self._hospitals.get_by_id(hospital_id)
        if hospital is None:
            raise NotFoundError(code="HOSPITAL_NOT_FOUND", message="Hospital not found.")
        return hospital

    async def get_default_hospital(self) -> Hospital:
        """Return the single MVP hospital, or fail if it has not been created yet."""
        hospital = await self._hospitals.get_first()
        if hospital is None:
            raise NotFoundError(
                code="HOSPITAL_NOT_CONFIGURED",
                message="No hospital profile exists yet. Create the hospital first.",
            )
        return hospital

    async def update_hospital(self, hospital_id: uuid.UUID, payload: HospitalUpdate) -> Hospital:
        hospital = await self.get_hospital(hospital_id)
        fields = payload.model_dump(exclude_unset=True)
        hospital = await self._hospitals.update(hospital, fields)
        logger.info(
            "hospital updated",
            extra={"extra_fields": {"hospital_id": str(hospital.id), "fields": list(fields)}},
        )
        return hospital

    async def get_settings(self, hospital_id: uuid.UUID) -> HospitalSettings:
        hospital = await self.get_hospital(hospital_id)
        return HospitalSettings.model_validate(hospital.settings or {})

    async def update_settings(
        self, hospital_id: uuid.UUID, payload: HospitalSettings
    ) -> HospitalSettings:
        hospital = await self.get_hospital(hospital_id)
        await self._hospitals.update(hospital, {"settings": payload.model_dump(mode="json")})
        logger.info(
            "hospital settings updated",
            extra={"extra_fields": {"hospital_id": str(hospital.id)}},
        )
        return payload
