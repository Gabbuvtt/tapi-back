"""
User repository — PostgreSQL implementation.

Implements the UserRepository interface using SQLAlchemy async sessions.
Handles mapping between domain entities and ORM models.
"""

from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.user import User
from domain.repositories.user_repository import UserRepository
from infraestructure.database.postgres.models import (
    NfcScanModel,
    UserModel,
)


class PostgresUserRepository(UserRepository):
    """Concrete user repository backed by PostgreSQL."""

    def __init__(self, session: AsyncSession):
        self._session = session

    # ── Mappers ─────────────────────────────────────────

    @staticmethod
    def _to_entity(model: UserModel) -> User:
        """Convert ORM model to domain entity."""
        return User(
            id=model.id,
            email=model.email,
            full_name=model.full_name,
            google_id=model.google_id,
            avatar_url=model.avatar_url,
            phone=model.phone,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def _to_model(entity: User) -> UserModel:
        """Convert domain entity to ORM model."""
        return UserModel(
            id=entity.id,
            email=entity.email,
            full_name=entity.full_name,
            google_id=entity.google_id,
            avatar_url=entity.avatar_url,
            phone=entity.phone,
            is_active=entity.is_active,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    # ── CRUD ────────────────────────────────────────────

    async def create(self, user: User) -> User:
        model = self._to_model(user)
        self._session.add(model)
        await self._session.flush()
        return self._to_entity(model)

    async def get_by_id(self, user_id: UUID) -> User | None:
        result = await self._session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_email(self, email: str) -> User | None:
        result = await self._session.execute(
            select(UserModel).where(UserModel.email == email)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_google_id(self, google_id: str) -> User | None:
        result = await self._session.execute(
            select(UserModel).where(UserModel.google_id == google_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def update(self, user: User) -> User:
        result = await self._session.execute(
            select(UserModel).where(UserModel.id == user.id)
        )
        model = result.scalar_one_or_none()
        if model:
            model.email = user.email
            model.full_name = user.full_name
            model.avatar_url = user.avatar_url
            model.phone = user.phone
            model.is_active = user.is_active
            model.updated_at = user.updated_at
            await self._session.flush()
            return self._to_entity(model)
        return user

    async def get_by_business(
        self, business_id: UUID, limit: int = 50, offset: int = 0
    ) -> list[User]:
        """Get users who have scanned NFC at this business."""
        result = await self._session.execute(
            select(UserModel)
            .join(NfcScanModel, NfcScanModel.user_id == UserModel.id)
            .where(NfcScanModel.business_id == business_id)
            .distinct()
            .limit(limit)
            .offset(offset)
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def get_inactive_users(
        self, business_id: UUID, inactive_days: int
    ) -> list[User]:
        """Get users who haven't scanned at the business in N days."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=inactive_days)

        # Subquery: users whose last scan is before the cutoff
        latest_scan = (
            select(
                NfcScanModel.user_id,
                func.max(NfcScanModel.scanned_at).label("last_scan"),
            )
            .where(NfcScanModel.business_id == business_id)
            .group_by(NfcScanModel.user_id)
        ).subquery()

        result = await self._session.execute(
            select(UserModel)
            .join(latest_scan, latest_scan.c.user_id == UserModel.id)
            .where(latest_scan.c.last_scan < cutoff)
        )
        return [self._to_entity(m) for m in result.scalars().all()]
