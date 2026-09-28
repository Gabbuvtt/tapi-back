"""
Business repository — PostgreSQL implementation.
"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.business import Business, BusinessMember
from domain.repositories.business_repository import BusinessRepository
from infraestructure.database.postgres.models import BusinessMemberModel, BusinessModel


class PostgresBusinessRepository(BusinessRepository):
    """Concrete business repository backed by PostgreSQL."""

    def __init__(self, session: AsyncSession):
        self._session = session

    # ── Mappers ─────────────────────────────────────────

    @staticmethod
    def _to_entity(model: BusinessModel) -> Business:
        return Business(
            id=model.id,
            name=model.name,
            slug=model.slug,
            email=model.email,
            phone=model.phone,
            address=model.address,
            google_place_id=model.google_place_id,
            logo_url=model.logo_url,
            category=model.category,
            is_active=model.is_active,
            owner_id=model.owner_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def _member_to_entity(model: BusinessMemberModel) -> BusinessMember:
        return BusinessMember(
            id=model.id,
            business_id=model.business_id,
            user_id=model.user_id,
            role=model.role,
            created_at=model.created_at,
        )

    # ── CRUD ────────────────────────────────────────────

    async def create(self, business: Business) -> Business:
        model = BusinessModel(
            id=business.id,
            name=business.name,
            slug=business.slug,
            email=business.email,
            phone=business.phone,
            address=business.address,
            google_place_id=business.google_place_id,
            logo_url=business.logo_url,
            category=business.category,
            is_active=business.is_active,
            owner_id=business.owner_id,
            created_at=business.created_at,
            updated_at=business.updated_at,
        )
        self._session.add(model)
        await self._session.flush()
        return self._to_entity(model)

    async def get_by_id(self, business_id: UUID) -> Business | None:
        result = await self._session.execute(
            select(BusinessModel).where(BusinessModel.id == business_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_slug(self, slug: str) -> Business | None:
        result = await self._session.execute(
            select(BusinessModel).where(BusinessModel.slug == slug)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def update(self, business: Business) -> Business:
        result = await self._session.execute(
            select(BusinessModel).where(BusinessModel.id == business.id)
        )
        model = result.scalar_one_or_none()
        if model:
            model.name = business.name
            model.slug = business.slug
            model.email = business.email
            model.phone = business.phone
            model.address = business.address
            model.google_place_id = business.google_place_id
            model.logo_url = business.logo_url
            model.category = business.category
            model.is_active = business.is_active
            model.updated_at = business.updated_at
            await self._session.flush()
            return self._to_entity(model)
        return business

    async def get_by_owner(self, owner_id: UUID) -> list[Business]:
        result = await self._session.execute(
            select(BusinessModel).where(BusinessModel.owner_id == owner_id)
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def add_member(self, member: BusinessMember) -> BusinessMember:
        model = BusinessMemberModel(
            id=member.id,
            business_id=member.business_id,
            user_id=member.user_id,
            role=member.role,
            created_at=member.created_at,
        )
        self._session.add(model)
        await self._session.flush()
        return self._member_to_entity(model)

    async def get_members(self, business_id: UUID) -> list[BusinessMember]:
        result = await self._session.execute(
            select(BusinessMemberModel).where(
                BusinessMemberModel.business_id == business_id
            )
        )
        return [self._member_to_entity(m) for m in result.scalars().all()]

    async def is_member(self, business_id: UUID, user_id: UUID) -> bool:
        result = await self._session.execute(
            select(BusinessMemberModel).where(
                BusinessMemberModel.business_id == business_id,
                BusinessMemberModel.user_id == user_id,
            )
        )
        return result.scalar_one_or_none() is not None
