"""Request and response schemas for department endpoints."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DepartmentCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=5000)


class DepartmentUpdate(BaseModel):
    """Partial update; omitted fields are left unchanged."""

    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=5000)


class DepartmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    hospital_id: uuid.UUID
    name: str
    description: str | None
    created_at: datetime
