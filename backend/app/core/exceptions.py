"""Application exceptions and standardized error responses.

All errors returned to clients follow the shape:

    {"success": false, "error": {"code": "...", "message": "..."}}

Internal details and stack traces are never exposed.
"""

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.logging import get_logger

logger = get_logger("app.errors")


class AppError(Exception):
    """Base class for expected application errors."""

    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


class UnauthorizedError(AppError):
    def __init__(
        self, code: str = "UNAUTHORIZED", message: str = "Authentication required."
    ) -> None:
        super().__init__(code, message, status.HTTP_401_UNAUTHORIZED)


class ForbiddenError(AppError):
    def __init__(self, code: str = "FORBIDDEN", message: str = "Insufficient permissions.") -> None:
        super().__init__(code, message, status.HTTP_403_FORBIDDEN)


class ConflictError(AppError):
    def __init__(self, code: str = "CONFLICT", message: str = "Resource already exists.") -> None:
        super().__init__(code, message, status.HTTP_409_CONFLICT)


class NotFoundError(AppError):
    def __init__(self, code: str = "NOT_FOUND", message: str = "Resource not found.") -> None:
        super().__init__(code, message, status.HTTP_404_NOT_FOUND)


class ServiceUnavailableError(AppError):
    def __init__(
        self,
        code: str = "SERVICE_UNAVAILABLE",
        message: str = "A required service is unavailable.",
    ) -> None:
        super().__init__(code, message, status.HTTP_503_SERVICE_UNAVAILABLE)


def error_response(code: str, message: str, status_code: int) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"success": False, "error": {"code": code, "message": message}},
    )


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def handle_app_error(request: Request, exc: AppError) -> JSONResponse:
        logger.warning(
            "application error",
            extra={"extra_fields": {"code": exc.code, "path": request.url.path}},
        )
        return error_response(exc.code, exc.message, exc.status_code)

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return error_response(
            "VALIDATION_ERROR",
            "Request validation failed.",
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    @app.exception_handler(StarletteHTTPException)
    async def handle_http_exception(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        return error_response("HTTP_ERROR", str(exc.detail), exc.status_code)

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("unhandled error", extra={"extra_fields": {"path": request.url.path}})
        return error_response(
            "INTERNAL_ERROR",
            "An unexpected error occurred.",
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
