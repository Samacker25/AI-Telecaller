"""Shared API dependencies for authentication and authorization."""

import uuid
from collections.abc import Callable, Coroutine
from typing import Annotated, Any

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.core.security import decode_access_token
from app.database.session import get_db
from app.models.user import User, UserRole
from app.services.auth_service import AuthService

_bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """Resolve the authenticated user from the Authorization: Bearer header."""
    if credentials is None:
        raise UnauthorizedError()

    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise UnauthorizedError(code="INVALID_TOKEN", message="Token is invalid or expired.")

    try:
        user_id = uuid.UUID(str(payload.get("sub")))
    except ValueError:
        raise UnauthorizedError(
            code="INVALID_TOKEN", message="Token is invalid or expired."
        ) from None

    user = await AuthService(db).get_active_user(user_id)
    if user is None:
        raise UnauthorizedError(code="INVALID_TOKEN", message="Token is invalid or expired.")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_roles(*roles: UserRole) -> Callable[..., Coroutine[Any, Any, User]]:
    """Dependency factory restricting an endpoint to the given roles."""
    allowed = {role.value for role in roles}

    async def dependency(current_user: CurrentUser) -> User:
        if current_user.role not in allowed:
            raise ForbiddenError()
        return current_user

    return dependency


AdminUser = Annotated[User, Depends(require_roles(UserRole.ADMIN))]
