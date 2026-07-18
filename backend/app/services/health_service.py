"""Health check business logic."""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger

logger = get_logger("app.services.health")


class HealthService:
    """Checks the availability of application dependencies."""

    async def check_database(self, session: AsyncSession) -> bool:
        """Return True if the database answers a trivial query."""
        try:
            await session.execute(text("SELECT 1"))
            return True
        except Exception:
            logger.exception("database readiness check failed")
            return False
