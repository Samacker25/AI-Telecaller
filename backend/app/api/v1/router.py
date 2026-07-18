"""Version 1 API router. Feature routers are registered here."""

from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.schemas.health import PingResponse

api_router = APIRouter()
api_router.include_router(auth_router)


@api_router.get("/ping", response_model=PingResponse, tags=["smoke"])
async def ping() -> PingResponse:
    """Smoke test endpoint for verifying API routing end to end."""
    return PingResponse(message="pong")
