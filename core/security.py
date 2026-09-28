"""
Security utilities for JWT token management and Google OAuth verification.
"""

from datetime import datetime, timedelta, timezone
from uuid import UUID

from jose import JWTError, jwt
import httpx

from core.config import settings
from core.exceptions import InvalidCredentialsError, TokenExpiredError


# ── Google OAuth2 Token Info Endpoint ───────────────────
GOOGLE_TOKEN_INFO_URL = "https://oauth2.googleapis.com/tokeninfo"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"


# ── JWT Helpers ─────────────────────────────────────────

def create_access_token(subject: str, role: str, extra: dict | None = None) -> str:
    """
    Create a short-lived JWT access token.

    Args:
        subject: The user ID (UUID as string).
        role: User role (customer, business_owner, admin).
        extra: Additional claims to include.

    Returns:
        Encoded JWT string.
    """
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {
        "sub": subject,
        "role": role,
        "type": "access",
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    if extra:
        payload.update(extra)

    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def create_refresh_token(subject: str) -> str:
    """
    Create a long-lived JWT refresh token.

    Args:
        subject: The user ID (UUID as string).

    Returns:
        Encoded JWT string.
    """
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
    )
    payload = {
        "sub": subject,
        "type": "refresh",
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def decode_token(token: str) -> dict:
    """
    Decode and validate a JWT token.

    Args:
        token: The JWT string to decode.

    Returns:
        Decoded payload as a dictionary.

    Raises:
        TokenExpiredError: If the token has expired.
        InvalidCredentialsError: If the token is malformed or invalid.
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except JWTError as e:
        if "expired" in str(e).lower():
            raise TokenExpiredError()
        raise InvalidCredentialsError(detail="Invalid token")


def verify_access_token(token: str) -> dict:
    """
    Verify that a token is a valid access token.

    Returns:
        Decoded payload with 'sub' (user_id) and 'role'.

    Raises:
        InvalidCredentialsError: If token type is not 'access'.
    """
    payload = decode_token(token)
    if payload.get("type") != "access":
        raise InvalidCredentialsError(detail="Invalid token type")
    return payload


def verify_refresh_token(token: str) -> dict:
    """
    Verify that a token is a valid refresh token.

    Returns:
        Decoded payload with 'sub' (user_id).

    Raises:
        InvalidCredentialsError: If token type is not 'refresh'.
    """
    payload = decode_token(token)
    if payload.get("type") != "refresh":
        raise InvalidCredentialsError(detail="Invalid token type")
    return payload


# ── Google OAuth2 Helpers ───────────────────────────────

async def verify_google_token(google_token: str) -> dict:
    """
    Verify a Google OAuth2 token and retrieve user information.

    The frontend sends the Google ID token obtained after the user
    signs in with Google. We verify it with Google's servers and
    extract user profile information.

    Args:
        google_token: The ID token from Google Sign-In.

    Returns:
        Dictionary with user info: email, name, picture, google_id (sub).

    Raises:
        InvalidCredentialsError: If the Google token is invalid.
    """
    async with httpx.AsyncClient() as client:
        # Step 1: Verify the token with Google
        response = await client.get(
            GOOGLE_TOKEN_INFO_URL,
            params={"id_token": google_token},
        )

        if response.status_code != 200:
            raise InvalidCredentialsError(detail="Invalid Google token")

        token_data = response.json()

        # Verify the token was issued for our application
        if token_data.get("aud") != settings.GOOGLE_CLIENT_ID:
            raise InvalidCredentialsError(
                detail="Google token not issued for this application"
            )

        return {
            "google_id": token_data["sub"],
            "email": token_data["email"],
            "full_name": token_data.get("name", ""),
            "avatar_url": token_data.get("picture", ""),
        }
