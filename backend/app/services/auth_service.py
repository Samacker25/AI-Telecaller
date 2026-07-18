"""Authentication business logic: registration, login, and identity lookup."""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, UnauthorizedError
from app.core.logging import get_logger
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse

logger = get_logger("app.services.auth")


class AuthService:
    """Handles user registration and JWT-based authentication."""

    def __init__(self, db: AsyncSession) -> None:
        self._users = UserRepository(db)

    async def register(self, payload: RegisterRequest) -> User:
        """Create a new account.

        The first registered user becomes the admin; later users are staff.
        """
        email = payload.email.lower()
        if await self._users.get_by_email(email) is not None:
            raise ConflictError(
                code="EMAIL_ALREADY_REGISTERED",
                message="An account with this email already exists.",
            )

        role = UserRole.ADMIN if await self._users.count() == 0 else UserRole.STAFF
        user = await self._users.create(
            name=payload.name,
            email=email,
            password_hash=hash_password(payload.password),
            role=role.value,
        )
        logger.info(
            "user registered",
            extra={"extra_fields": {"user_id": str(user.id), "role": user.role}},
        )
        return user

    async def login(self, payload: LoginRequest) -> TokenResponse:
        """Verify credentials and issue an access token."""
        user = await self._users.get_by_email(payload.email.lower())
        if user is None or not verify_password(payload.password, user.password_hash):
            # Same error for unknown email and wrong password to prevent enumeration.
            raise UnauthorizedError(
                code="INVALID_CREDENTIALS", message="Invalid email or password."
            )
        if not user.is_active:
            raise UnauthorizedError(code="ACCOUNT_DISABLED", message="This account is disabled.")

        token, expires_in = create_access_token(subject=str(user.id), role=user.role)
        logger.info("user logged in", extra={"extra_fields": {"user_id": str(user.id)}})
        return TokenResponse(access_token=token, expires_in=expires_in)

    async def list_users(self) -> list[User]:
        """Return all accounts, oldest first."""
        return await self._users.list_all()

    async def get_active_user(self, user_id: uuid.UUID) -> User | None:
        """Return the user for a token subject, or None if missing or disabled."""
        user = await self._users.get_by_id(user_id)
        if user is None or not user.is_active:
            return None
        return user
