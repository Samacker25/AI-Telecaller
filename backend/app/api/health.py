"""Health, readiness, and liveness endpoints.

Mounted at the application root (no /api/v1 prefix, no authentication)
so deployment platforms can probe them directly.
"""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.core.exceptions import ServiceUnavailableError
from app.database.session import get_db
from app.schemas.health import HealthResponse, ReadinessResponse
from app.services.health_service import HealthService

router = APIRouter(tags=["health"])


def get_health_service() -> HealthService:
    return HealthService()


@router.get("/health", response_model=HealthResponse)
async def health(settings: Annotated[Settings, Depends(get_settings)]) -> HealthResponse:
    """Basic process health: the API is up and serving requests."""
    return HealthResponse(
        status="ok",
        app=settings.app_name,
        version=settings.app_version,
        environment=settings.app_env,
    )


@router.get("/live")
async def live() -> dict[str, str]:
    """Liveness probe: process is alive."""
    return {"status": "alive"}


@router.get("/ready", response_model=ReadinessResponse)
async def ready(
    session: Annotated[AsyncSession, Depends(get_db)],
    service: Annotated[HealthService, Depends(get_health_service)],
) -> ReadinessResponse:
    """Readiness probe: process can reach its dependencies (database)."""
    database_ok = await service.check_database(session)
    if not database_ok:
        raise ServiceUnavailableError(
            code="DATABASE_UNAVAILABLE",
            message="Database connection failed.",
        )
    return ReadinessResponse(status="ready", database="ok")
