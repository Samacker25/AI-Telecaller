"""Hospital endpoints: profile CRUD and settings. Reads are public; writes are admin-only."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import AdminUser, CurrentUser
from app.database.session import get_db
from app.schemas.hospital import (
    HospitalCreate,
    HospitalResponse,
    HospitalSettings,
    HospitalUpdate,
)
from app.services.hospital_service import HospitalService

router = APIRouter(prefix="/hospitals", tags=["hospitals"])

DbSession = Annotated[AsyncSession, Depends(get_db)]


@router.get("", response_model=list[HospitalResponse])
async def list_hospitals(db: DbSession) -> list[HospitalResponse]:
    """List hospital profiles. Public."""
    hospitals = await HospitalService(db).list_hospitals()
    return [HospitalResponse.model_validate(hospital) for hospital in hospitals]


@router.post("", response_model=HospitalResponse, status_code=status.HTTP_201_CREATED)
async def create_hospital(
    payload: HospitalCreate, admin: AdminUser, db: DbSession
) -> HospitalResponse:
    """Create the hospital profile. Admin only; the MVP allows exactly one."""
    hospital = await HospitalService(db).create_hospital(payload)
    return HospitalResponse.model_validate(hospital)


@router.get("/{hospital_id}", response_model=HospitalResponse)
async def get_hospital(hospital_id: uuid.UUID, db: DbSession) -> HospitalResponse:
    """Return a hospital profile. Public."""
    hospital = await HospitalService(db).get_hospital(hospital_id)
    return HospitalResponse.model_validate(hospital)


@router.put("/{hospital_id}", response_model=HospitalResponse)
async def update_hospital(
    hospital_id: uuid.UUID, payload: HospitalUpdate, admin: AdminUser, db: DbSession
) -> HospitalResponse:
    """Update the hospital profile. Admin only."""
    hospital = await HospitalService(db).update_hospital(hospital_id, payload)
    return HospitalResponse.model_validate(hospital)


@router.get("/{hospital_id}/settings", response_model=HospitalSettings)
async def get_hospital_settings(
    hospital_id: uuid.UUID, current_user: CurrentUser, db: DbSession
) -> HospitalSettings:
    """Return hospital settings (working hours, contacts). Authenticated users only."""
    return await HospitalService(db).get_settings(hospital_id)


@router.put("/{hospital_id}/settings", response_model=HospitalSettings)
async def update_hospital_settings(
    hospital_id: uuid.UUID, payload: HospitalSettings, admin: AdminUser, db: DbSession
) -> HospitalSettings:
    """Replace hospital settings. Admin only."""
    return await HospitalService(db).update_settings(hospital_id, payload)
