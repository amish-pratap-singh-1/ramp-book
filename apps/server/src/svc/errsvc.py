"""
Error Service Module
"""

import logging
from typing import Optional

from fastapi import Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class AppError(Exception):
    """
    Base application error.
    All custom errors derive from this.
    Automatically logs itself at ERROR level when raised.
    """

    http_code: int = 500
    default_detail: str = "An unexpected error occurred"

    def __init__(
        self,
        detail: Optional[str] = None,
        http_code: Optional[int] = None,
    ):
        self.detail = detail or self.default_detail
        self.http_code = http_code or self.__class__.http_code

        super().__init__(self.detail)
        self._log()

    def _log(self) -> None:
        logger.error(
            "[%s] HTTP %s — %s",
            self.__class__.__name__,
            self.http_code,
            self.detail,
            exc_info=True,
        )


# ── 400 Bad Request ─────────────────────────────────────────────────────────


class BadRequestError(AppError):
    """Base class for 400 Bad Request errors."""

    http_code = 400
    default_detail = "Bad request"


class ValidationError(BadRequestError):
    """Raised when request validation fails."""

    default_detail = "Validation failed"


class MissingFieldError(BadRequestError):
    """Raised when a required field is missing in the request."""

    default_detail = "A required field is missing"


# ── 401 Unauthorised ────────────────────────────────────────────────────────


class UnauthorisedError(AppError):
    """Base class for 401 Unauthorized errors."""

    http_code = 401
    default_detail = "Authentication required"


class InvalidTokenError(UnauthorisedError):
    """Raised when an authentication token is invalid or expired."""

    default_detail = "Token is invalid or expired"


class InvalidCredentialsError(UnauthorisedError):
    """Raised when login credentials are incorrect."""

    default_detail = "Incorrect username or password"


# ── 403 Forbidden ───────────────────────────────────────────────────────────


class ForbiddenError(AppError):
    """Base class for 403 Forbidden errors."""

    http_code = 403
    default_detail = "You do not have permission to perform this action"


class InsufficientRoleError(ForbiddenError):
    """Raised when the user's role is insufficient to access a resource."""

    default_detail = "Your role does not grant access to this resource"


# ── 404 Not Found ───────────────────────────────────────────────────────────


class NotFoundError(AppError):
    """Base class for 404 Not Found errors."""

    http_code = 404
    default_detail = "Resource not found"


class UserNotFoundError(NotFoundError):
    """Raised when a requested user cannot be found."""

    default_detail = "User not found"


class ResourceNotFoundError(NotFoundError):
    """Raised when a requested resource does not exist."""

    default_detail = "The requested resource does not exist"


# ── 409 Conflict ────────────────────────────────────────────────────────────


class ConflictError(AppError):
    """Base class for 409 Conflict errors."""

    http_code = 409
    default_detail = "Conflict with current state of the resource"


class DuplicateEntryError(ConflictError):
    """Raised when attempting to create a duplicate record."""

    default_detail = "A record with this value already exists"


# ── 422 Unprocessable ───────────────────────────────────────────────────────


class UnprocessableError(AppError):
    """Base class for 422 Unprocessable Entity errors."""

    http_code = 422
    default_detail = "Unable to process the request"


# ── 500 Internal ────────────────────────────────────────────────────────────


class InternalError(AppError):
    """Base class for 500 Internal Server errors."""

    http_code = 500
    default_detail = "An internal server error occurred"


class DatabaseError(InternalError):
    """Raised when a database operation fails."""

    default_detail = "A database error occurred"


class ExternalServiceError(InternalError):
    """Raised when an external service call fails."""

    default_detail = "An external service is unavailable"


class ErrSvc:
    """Class to handle errors"""

    @staticmethod
    def handle_api_error(e: Exception) -> AppError:
        """
        Converts any exception to an AppError.
        If it's already an AppError, returns it.
        Otherwise, returns it as a generic AppError.
        """
        if isinstance(e, AppError):
            return e
        return AppError(detail=str(e))

    @staticmethod
    async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
        """
        Central exception handler for all AppError subclasses.

        Register once in main.py:

            app.add_exception_handler(AppError, ErrSvc.app_error_handler)
        """
        return JSONResponse(
            status_code=exc.http_code,
            content={"error": exc.__class__.__name__, "detail": exc.detail},
        )
