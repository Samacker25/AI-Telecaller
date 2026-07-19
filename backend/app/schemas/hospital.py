"""Request and response schemas for hospital endpoints."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.schemas.schedule import WeeklySchedule


class HospitalCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    address: str | None = Field(default=None, max_length=2000)
    phone: str | None = Field(default=None, max_length=50)
    email: EmailStr | None = Field(default=None, max_length=320)
    website: str | None = Field(default=None, max_length=500)


class HospitalUpdate(BaseModel):
    """Partial update; omitted fields are left unchanged."""

    name: str | None = Field(default=None, min_length=1, max_length=255)
    address: str | None = Field(default=None, max_length=2000)
    phone: str | None = Field(default=None, max_length=50)
    email: EmailStr | None = Field(default=None, max_length=320)
    website: str | None = Field(default=None, max_length=500)


class HospitalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    address: str | None
    phone: str | None
    email: EmailStr | None
    website: str | None
    created_at: datetime


class HospitalSettings(BaseModel):
    """Operational settings stored as JSON on the hospital record."""

    model_config = ConfigDict(extra="forbid")

    working_hours: WeeklySchedule | None = None
    emergency_contact: str | None = Field(default=None, max_length=50)
    escalation_email: EmailStr | None = Field(default=None, max_length=320)
