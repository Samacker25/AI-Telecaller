"""Health and readiness response schemas."""

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    app: str
    version: str
    environment: str


class ReadinessResponse(BaseModel):
    status: str
    database: str


class PingResponse(BaseModel):
    message: str
