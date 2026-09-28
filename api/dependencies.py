"""
FastAPI dependencies for dependency injection.

Provides:
- Database session dependencies (PostgreSQL, MongoDB).
- Current user authentication dependency.
- Repository and service factory dependencies.
- Redis cache dependency.
"""

from uuid import UUID

from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from core.exceptions import InvalidCredentialsError
from core.security import verify_access_token
from domain.repositories.user_repository import UserRepository
from domain.repositories.business_repository import BusinessRepository
from domain.repositories.loyalty_repository import LoyaltyRepository
from domain.repositories.nfc_repository import NfcRepository
from domain.repositories.review_repository import ReviewRepository
from domain.repositories.notification_repository import NotificationRepository
from domain.repositories.menu_repository import MenuRepository
from domain.services.auth_service import AuthService
from domain.services.review_service import ReviewService
from domain.services.loyalty_service import LoyaltyService
from domain.services.nfc_service import NfcService
from domain.services.notification_service import NotificationService
from domain.services.metrics_service import MetricsService
from infraestructure.database.postgres.connection import get_postgres_session
from infraestructure.database.postgres.repositories.user_repo import PostgresUserRepository
from infraestructure.database.postgres.repositories.business_repo import PostgresBusinessRepository
from infraestructure.database.postgres.repositories.loyalty_repo import PostgresLoyaltyRepository
from infraestructure.database.postgres.repositories.nfc_repo import PostgresNfcRepository
from infraestructure.database.mongodb.connection import get_mongodb
from infraestructure.database.mongodb.repositories.review_repo import MongoReviewRepository
from infraestructure.database.mongodb.repositories.menu_repo import MongoMenuRepository
from infraestructure.cache.redis_cache import get_redis, RedisCache


# ── Database Sessions ───────────────────────────────────

async def get_db(session: AsyncSession = Depends(get_postgres_session)):
    """PostgreSQL session dependency."""
    return session


def get_mongo_db():
    """MongoDB database dependency."""
    return get_mongodb()


# ── Repository Dependencies ────────────────────────────

def get_user_repo(db: AsyncSession = Depends(get_db)) -> UserRepository:
    return PostgresUserRepository(db)


def get_business_repo(db: AsyncSession = Depends(get_db)) -> BusinessRepository:
    return PostgresBusinessRepository(db)


def get_loyalty_repo(db: AsyncSession = Depends(get_db)) -> LoyaltyRepository:
    return PostgresLoyaltyRepository(db)


def get_nfc_repo(db: AsyncSession = Depends(get_db)) -> NfcRepository:
    return PostgresNfcRepository(db)


def get_review_repo() -> ReviewRepository:
    db = get_mongo_db()
    return MongoReviewRepository(db)


def get_menu_repo() -> MenuRepository:
    db = get_mongo_db()
    return MongoMenuRepository(db)


def get_cache() -> RedisCache:
    return RedisCache(get_redis())


# ── Service Dependencies ───────────────────────────────

def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repo),
) -> AuthService:
    return AuthService(user_repo)


def get_review_service(
    review_repo: ReviewRepository = Depends(get_review_repo),
) -> ReviewService:
    return ReviewService(review_repo)


def get_loyalty_service(
    loyalty_repo: LoyaltyRepository = Depends(get_loyalty_repo),
) -> LoyaltyService:
    return LoyaltyService(loyalty_repo)


def get_nfc_service(
    nfc_repo: NfcRepository = Depends(get_nfc_repo),
    business_repo: BusinessRepository = Depends(get_business_repo),
    loyalty_service: LoyaltyService = Depends(get_loyalty_service),
) -> NfcService:
    return NfcService(nfc_repo, business_repo, loyalty_service)


def get_notification_service(
    db: AsyncSession = Depends(get_db),
) -> NotificationService:
    from infraestructure.database.postgres.repositories.user_repo import PostgresUserRepository
    from infraestructure.database.postgres.repositories.notification_repo import PostgresNotificationRepository
    notification_repo = PostgresNotificationRepository(db)
    user_repo = PostgresUserRepository(db)
    return NotificationService(notification_repo, user_repo)


def get_metrics_service(
    nfc_repo: NfcRepository = Depends(get_nfc_repo),
    review_repo: ReviewRepository = Depends(get_review_repo),
    loyalty_repo: LoyaltyRepository = Depends(get_loyalty_repo),
) -> MetricsService:
    return MetricsService(nfc_repo, review_repo, loyalty_repo)


# ── Authentication Dependencies ─────────────────────────

async def get_current_user_id(
    authorization: str = Header(..., description="Bearer <token>"),
) -> UUID:
    """
    Extract and validate the current user from the Authorization header.

    Usage:
        @router.get("/me")
        async def me(user_id: UUID = Depends(get_current_user_id)):
            ...
    """
    if not authorization.startswith("Bearer "):
        raise InvalidCredentialsError(detail="Invalid authorization header format")

    token = authorization[7:]  # Remove "Bearer " prefix
    payload = verify_access_token(token)
    user_id = payload.get("sub")

    if not user_id:
        raise InvalidCredentialsError(detail="Invalid token payload")

    return UUID(user_id)


async def get_current_user_role(
    authorization: str = Header(..., description="Bearer <token>"),
) -> dict:
    """
    Extract user ID and role from the JWT token.

    Returns:
        dict with 'user_id' (UUID) and 'role' (str).
    """
    if not authorization.startswith("Bearer "):
        raise InvalidCredentialsError(detail="Invalid authorization header format")

    token = authorization[7:]
    payload = verify_access_token(token)

    return {
        "user_id": UUID(payload["sub"]),
        "role": payload.get("role", "customer"),
    }
