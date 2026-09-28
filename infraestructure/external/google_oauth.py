"""
Google OAuth2 client.

Handles server-side verification of Google ID tokens.
The main logic is in core/security.py; this module provides
additional helpers if needed.
"""

import httpx

from core.config import settings
from core.exceptions import ExternalServiceError


GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"


async def get_google_user_info(access_token: str) -> dict:
    """
    Fetch user info from Google using an access token.

    This is an alternative to ID token verification, useful when
    the frontend provides an access token instead of an ID token.

    Args:
        access_token: Google OAuth2 access token.

    Returns:
        dict with user profile data.

    Raises:
        ExternalServiceError: If Google API is unavailable.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        if response.status_code != 200:
            raise ExternalServiceError(
                service="Google OAuth",
                detail=f"Failed to fetch user info: {response.status_code}",
            )

        data = response.json()
        return {
            "google_id": data["sub"],
            "email": data["email"],
            "full_name": data.get("name", ""),
            "avatar_url": data.get("picture", ""),
        }
