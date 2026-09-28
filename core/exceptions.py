"""
Custom exception classes for the TAPI application.

Each exception maps to an HTTP status code and provides a consistent
error response format across the entire API.
"""

from fastapi import HTTPException, status


class TapiException(HTTPException):
    """Base exception for all TAPI-specific errors."""

    def __init__(
        self,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail: str = "An unexpected error occurred",
    ):
        super().__init__(status_code=status_code, detail=detail)


# ── Authentication Errors ───────────────────────────────

class InvalidCredentialsError(TapiException):
    """Raised when authentication credentials are invalid."""

    def __init__(self, detail: str = "Invalid credentials"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
        )


class TokenExpiredError(TapiException):
    """Raised when a JWT token has expired."""

    def __init__(self, detail: str = "Token has expired"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
        )


class InsufficientPermissionsError(TapiException):
    """Raised when a user lacks the required role or permission."""

    def __init__(self, detail: str = "Insufficient permissions"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )


# ── Resource Errors ─────────────────────────────────────

class NotFoundError(TapiException):
    """Raised when a requested resource does not exist."""

    def __init__(self, resource: str = "Resource", detail: str | None = None):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail or f"{resource} not found",
        )


class AlreadyExistsError(TapiException):
    """Raised when trying to create a resource that already exists."""

    def __init__(self, resource: str = "Resource", detail: str | None = None):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail or f"{resource} already exists",
        )


# ── Business Logic Errors ──────────────────────────────

class BusinessLogicError(TapiException):
    """Raised when a business rule is violated."""

    def __init__(self, detail: str = "Business rule violation"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
        )


class InsufficientPointsError(BusinessLogicError):
    """Raised when a user doesn't have enough points/visits to redeem."""

    def __init__(self, detail: str = "Insufficient points or visits for this reward"):
        super().__init__(detail=detail)


class RewardOutOfStockError(BusinessLogicError):
    """Raised when a reward has no available stock."""

    def __init__(self, detail: str = "This reward is out of stock"):
        super().__init__(detail=detail)


# ── External Service Errors ─────────────────────────────

class ExternalServiceError(TapiException):
    """Raised when an external service (Google, SendGrid) fails."""

    def __init__(self, service: str, detail: str | None = None):
        super().__init__(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=detail or f"External service '{service}' is unavailable",
        )
