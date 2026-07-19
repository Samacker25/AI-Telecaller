"""Request and response schemas for knowledge document endpoints."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.document import DocumentStatus


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    hospital_id: uuid.UUID
    file_name: str
    file_type: str
    status: DocumentStatus
    chunk_count: int
    error_message: str | None
    uploaded_by: uuid.UUID | None
    created_at: datetime
    updated_at: datetime


class DocumentUploadResponse(BaseModel):
    """Upload acknowledgement per the API specification."""

    document_id: uuid.UUID
    status: DocumentStatus
