"""Version 1 API router. Feature routers are registered here."""

from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.chat import router as chat_router
from app.api.v1.conversations import router as conversations_router
from app.api.v1.departments import router as departments_router
from app.api.v1.doctors import router as doctors_router
from app.api.v1.documents import router as documents_router
from app.api.v1.hospitals import router as hospitals_router
from app.schemas.health import PingResponse

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(hospitals_router)
api_router.include_router(departments_router)
api_router.include_router(doctors_router)
api_router.include_router(documents_router)
api_router.include_router(chat_router)
api_router.include_router(conversations_router)


@api_router.get("/ping", response_model=PingResponse, tags=["smoke"])
async def ping() -> PingResponse:
    """Smoke test endpoint for verifying API routing end to end."""
    return PingResponse(message="pong")
