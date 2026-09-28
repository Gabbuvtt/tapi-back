"""
Auth API endpoints.

POST /auth/google  — Login/register with Google OAuth
POST /auth/refresh — Refresh access token
GET  /auth/me      — Get current user profile
"""

from uuid import UUID

from fastapi import APIRouter, Depends

from api.dependencies import get_auth_service, get_current_user_id
from api.v1.auth.schemas import (
    GoogleAuthRequest,
    MessageResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    TokenResponse,
    UserResponse,
)
from domain.services.auth_service import AuthService

router = APIRouter()


@router.post(
    "/google",
    response_model=TokenResponse,
    summary="Login with Google OAuth",
    description="Authenticate using a Google OAuth ID token. Creates a new user if they don't exist.",
)
async def google_login(
    request: GoogleAuthRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    result = await auth_service.google_login(request.google_token)
    user = result["user"]

    return TokenResponse(
        access_token=result["access_token"],
        refresh_token=result["refresh_token"],
        token_type=result["token_type"],
        expires_in=result["expires_in"],
        user=UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            avatar_url=user.avatar_url,
            created_at=user.created_at,
        ),
    )


@router.post(
    "/refresh",
    response_model=RefreshTokenResponse,
    summary="Refresh access token",
    description="Exchange a valid refresh token for a new access/refresh token pair.",
)
async def refresh_token(
    request: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    result = await auth_service.refresh_tokens(request.refresh_token)
    return RefreshTokenResponse(**result)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    description="Retrieve the profile of the currently authenticated user.",
)
async def get_me(
    user_id: UUID = Depends(get_current_user_id),
    auth_service: AuthService = Depends(get_auth_service),
):
    user = await auth_service.get_current_user(user_id)
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        avatar_url=user.avatar_url,
        created_at=user.created_at,
    )


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Logout",
    description="Invalidate the current session. Client should discard tokens.",
)
async def logout(
    user_id: UUID = Depends(get_current_user_id),
):
    # JWT is stateless — client-side token removal.
    # For enhanced security, implement a token blacklist in Redis.
    return MessageResponse(message="Logged out successfully")
