"""
Pydantic schemas for the Auth module.

These define the request/response contracts for the API.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


# ── Requests ────────────────────────────────────────────

class GoogleAuthRequest(BaseModel):
    """Request body for Google OAuth login."""
    google_token: str = Field(..., description="Google OAuth ID token from frontend")


class RefreshTokenRequest(BaseModel):
    """Request body for token refresh."""
    refresh_token: str = Field(..., description="Current refresh token")


# ── Responses ───────────────────────────────────────────

class UserResponse(BaseModel):
    """Public user profile data."""
    id: UUID
    email: str
    full_name: str
    avatar_url: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """JWT token pair response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = Field(description="Token validity in seconds")
    user: UserResponse


class RefreshTokenResponse(BaseModel):
    """Response for token refresh."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class MessageResponse(BaseModel):
    """Generic message response."""
    message: str
