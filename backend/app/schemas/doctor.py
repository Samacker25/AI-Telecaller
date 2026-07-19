"""Request and response schemas for doctor endpoints."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.schedule import WeeklySchedule


class DoctorCreate(BaseModel):
    department_id: uuid.UUID
    name: str = Field(min_length=1, max_length=255)
    specialization: str = Field(min_length=1, max_length=255)
    qualification: str | None = Field(default=None, max_length=255)
    opd_schedule: WeeklySchedule | None = None
    is_available: bool = True


class DoctorUpdate(BaseModel):
    """Partial update; omitted fields are left unchanged."""

    department_id: uuid.UUID | None = None
    name: str | None = Field(default=None, min_length=1, max_length=255)
    specialization: str | None = Field(default=None, min_length=1, max_length=255)
    qualification: str | None = Field(default=None, max_length=255)
    opd_schedule: WeeklySchedule | None = None
    is_available: bool | None = None


class DoctorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    hospital_id: uuid.UUID
    department_id: uuid.UUID
    name: str
    specialization: str
    qualification: str | None
    opd_schedule: WeeklySchedule | None
    is_available: bool
    created_at: datetime
