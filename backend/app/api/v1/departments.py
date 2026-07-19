"""Department endpoints. Reads are public; writes are admin-only."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import AdminUser
from app.database.session import get_db
from app.schemas.department import DepartmentCreate, DepartmentResponse, DepartmentUpdate
from app.services.department_service import DepartmentService

router = APIRouter(prefix="/departments", tags=["departments"])

DbSession = Annotated[AsyncSession, Depends(get_db)]


@router.get("", response_model=list[DepartmentResponse])
async def list_departments(db: DbSession) -> list[DepartmentResponse]:
    """List departments. Public."""
    departments = await DepartmentService(db).list_departments()
    return [DepartmentResponse.model_validate(department) for department in departments]


@router.post("", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
async def create_department(
    payload: DepartmentCreate, admin: AdminUser, db: DbSession
) -> DepartmentResponse:
    """Create a department. Admin only."""
    department = await DepartmentService(db).create_department(payload)
    return DepartmentResponse.model_validate(department)


@router.get("/{department_id}", response_model=DepartmentResponse)
async def get_department(department_id: uuid.UUID, db: DbSession) -> DepartmentResponse:
    """Return a department. Public."""
    department = await DepartmentService(db).get_department(department_id)
    return DepartmentResponse.model_validate(department)


@router.put("/{department_id}", response_model=DepartmentResponse)
async def update_department(
    department_id: uuid.UUID, payload: DepartmentUpdate, admin: AdminUser, db: DbSession
) -> DepartmentResponse:
    """Update a department. Admin only."""
    department = await DepartmentService(db).update_department(department_id, payload)
    return DepartmentResponse.model_validate(department)


@router.delete("/{department_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_department(department_id: uuid.UUID, admin: AdminUser, db: DbSession) -> None:
    """Delete a department without doctors. Admin only."""
    await DepartmentService(db).delete_department(department_id)
