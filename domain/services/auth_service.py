"""
Auth service — handles Google OAuth login/register and JWT token management.

Orchestrates the authentication flow:
1. Verify Google token → get user info
2. Find or create user in database
3. Generate JWT access + refresh tokens
"""

from uuid import UUID

from core.security import (
    create_access_token,
    create_refresh_token,
    verify_google_token,
    verify_refresh_token,
)
from core.constants import UserRole
from core.exceptions import InvalidCredentialsError, NotFoundError
from domain.entities.user import User
from domain.repositories.user_repository import UserRepository


class AuthService:
    """Service for authentication and authorization logic."""

    def __init__(self, user_repo: UserRepository):
        self._user_repo = user_repo

    async def google_login(self, google_token: str) -> dict:
        """
        Authenticate a user with a Google OAuth token.

        If the user doesn't exist, they are registered automatically.

        Args:
            google_token: The ID token from Google Sign-In.

        Returns:
            dict with access_token, refresh_token, token_type,
            expires_in, and user data.
        """
        # Step 1: Verify with Google
        google_data = await verify_google_token(google_token)

        # Step 2: Find or create user
        user = await self._user_repo.get_by_google_id(google_data["google_id"])

        if user is None:
            user = User(
                email=google_data["email"],
                full_name=google_data["full_name"],
                google_id=google_data["google_id"],
                avatar_url=google_data["avatar_url"],
            )
            user = await self._user_repo.create(user)
        else:
            # Update profile info from Google (name, avatar may change)
            user.full_name = google_data["full_name"]
            user.avatar_url = google_data["avatar_url"]
            user = await self._user_repo.update(user)

        # Step 3: Determine role (check if they own any business)
        role = UserRole.CUSTOMER

        # Step 4: Generate JWT tokens
        access_token = create_access_token(
            subject=str(user.id),
            role=role,
        )
        refresh_token = create_refresh_token(subject=str(user.id))

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 1800,  # 30 minutes in seconds
            "user": user,
        }

    async def refresh_tokens(self, refresh_token_str: str) -> dict:
        """
        Generate new access/refresh tokens from a valid refresh token.

        Args:
            refresh_token_str: The current refresh token.

        Returns:
            dict with new access_token and refresh_token.

        Raises:
            InvalidCredentialsError: If the refresh token is invalid.
        """
        payload = verify_refresh_token(refresh_token_str)
        user_id = payload.get("sub")

        if not user_id:
            raise InvalidCredentialsError(detail="Invalid refresh token payload")

        user = await self._user_repo.get_by_id(UUID(user_id))
        if user is None:
            raise NotFoundError(resource="User")

        role = UserRole.CUSTOMER

        access_token = create_access_token(subject=str(user.id), role=role)
        new_refresh_token = create_refresh_token(subject=str(user.id))

        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
            "expires_in": 1800,
        }

    async def get_current_user(self, user_id: UUID) -> User:
        """
        Retrieve the current authenticated user.

        Args:
            user_id: The user ID from the JWT token.

        Returns:
            User entity.

        Raises:
            NotFoundError: If the user doesn't exist.
        """
        user = await self._user_repo.get_by_id(user_id)
        if user is None:
            raise NotFoundError(resource="User")
        return user
