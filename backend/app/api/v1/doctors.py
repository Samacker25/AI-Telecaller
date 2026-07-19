"""Doctor endpoints. Reads are public with filters; writes are admin-only."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import AdminUser
from app.database.session import get_db
from app.schemas.doctor import DoctorCreate, DoctorResponse, DoctorUpdate
from app.services.doctor_service import DoctorService

router = APIRouter(prefix="/doctors", tags=["doctors"])

DbSession = Annotated[AsyncSession, Depends(get_db)]


@router.get("", response_model=list[DoctorResponse])
async def list_doctors(
    db: DbSession,
    department_id: Annotated[uuid.UUID | None, Query()] = None,
    specialization: Annotated[str | None, Query(max_length=255)] = None,
    available: Annotated[bool | None, Query()] = None,
) -> list[DoctorResponse]:
    """List doctors, optionally filtered by department, specialization, or availability. Public."""
    doctors = await DoctorService(db).list_doctors(
        department_id=department_id,
        specialization=specialization,
        available=available,
    )
    return [DoctorResponse.model_validate(doctor) for doctor in doctors]


@router.post("", response_model=DoctorResponse, status_code=status.HTTP_201_CREATED)
async def create_doctor(payload: DoctorCreate, admin: AdminUser, db: DbSession) -> DoctorResponse:
    """Create a doctor in a department. Admin only."""
    doctor = await DoctorService(db).create_doctor(payload)
    return DoctorResponse.model_validate(doctor)


@router.get("/{doctor_id}", response_model=DoctorResponse)
async def get_doctor(doctor_id: uuid.UUID, db: DbSession) -> DoctorResponse:
    """Return a doctor. Public."""
    doctor = await DoctorService(db).get_doctor(doctor_id)
    return DoctorResponse.model_validate(doctor)


@router.put("/{doctor_id}", response_model=DoctorResponse)
async def update_doctor(
    doctor_id: uuid.UUID, payload: DoctorUpdate, admin: AdminUser, db: DbSession
) -> DoctorResponse:
    """Update a doctor. Admin only."""
    doctor = await DoctorService(db).update_doctor(doctor_id, payload)
    return DoctorResponse.model_validate(doctor)


@router.delete("/{doctor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_doctor(doctor_id: uuid.UUID, admin: AdminUser, db: DbSession) -> None:
    """Delete a doctor. Admin only."""
    await DoctorService(db).delete_doctor(doctor_id)
