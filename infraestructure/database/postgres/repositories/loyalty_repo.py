"""
Loyalty repository — PostgreSQL implementation.
"""

from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.loyalty import LoyaltyCard, LoyaltyProgram
from domain.entities.reward import Redemption, Reward
from domain.repositories.loyalty_repository import LoyaltyRepository
from infraestructure.database.postgres.models import (
    LoyaltyCardModel,
    LoyaltyProgramModel,
    RedemptionModel,
    RewardModel,
)


class PostgresLoyaltyRepository(LoyaltyRepository):
    """Concrete loyalty repository backed by PostgreSQL."""

    def __init__(self, session: AsyncSession):
        self._session = session

    # ── Program Mappers ─────────────────────────────────

    @staticmethod
    def _program_to_entity(model: LoyaltyProgramModel) -> LoyaltyProgram:
        return LoyaltyProgram(
            id=model.id, business_id=model.business_id, name=model.name,
            program_type=model.program_type, visits_required=model.visits_required,
            points_per_visit=model.points_per_visit, is_active=model.is_active,
            created_at=model.created_at, updated_at=model.updated_at,
        )

    @staticmethod
    def _card_to_entity(model: LoyaltyCardModel) -> LoyaltyCard:
        return LoyaltyCard(
            id=model.id, user_id=model.user_id, program_id=model.program_id,
            business_id=model.business_id, current_visits=model.current_visits,
            current_points=model.current_points, total_visits=model.total_visits,
            total_points=model.total_points, status=model.status,
            last_visit_at=model.last_visit_at, created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def _reward_to_entity(model: RewardModel) -> Reward:
        return Reward(
            id=model.id, program_id=model.program_id, business_id=model.business_id,
            title=model.title, description=model.description, reward_type=model.reward_type,
            value=model.value, points_cost=model.points_cost, visits_cost=model.visits_cost,
            stock=model.stock, is_active=model.is_active, created_at=model.created_at,
        )

    @staticmethod
    def _redemption_to_entity(model: RedemptionModel) -> Redemption:
        return Redemption(
            id=model.id, reward_id=model.reward_id, user_id=model.user_id,
            business_id=model.business_id, code=model.code, status=model.status,
            redeemed_at=model.redeemed_at, expires_at=model.expires_at, used_at=model.used_at,
        )

    # ── Programs ────────────────────────────────────────

    async def create_program(self, program: LoyaltyProgram) -> LoyaltyProgram:
        model = LoyaltyProgramModel(
            id=program.id, business_id=program.business_id, name=program.name,
            program_type=program.program_type, visits_required=program.visits_required,
            points_per_visit=program.points_per_visit, is_active=program.is_active,
        )
        self._session.add(model)
        await self._session.flush()
        return self._program_to_entity(model)

    async def get_program(self, program_id: UUID) -> LoyaltyProgram | None:
        result = await self._session.execute(
            select(LoyaltyProgramModel).where(LoyaltyProgramModel.id == program_id)
        )
        model = result.scalar_one_or_none()
        return self._program_to_entity(model) if model else None

    async def get_program_by_business(self, business_id: UUID) -> LoyaltyProgram | None:
        result = await self._session.execute(
            select(LoyaltyProgramModel).where(
                LoyaltyProgramModel.business_id == business_id,
                LoyaltyProgramModel.is_active == True,
            )
        )
        model = result.scalar_one_or_none()
        return self._program_to_entity(model) if model else None

    async def update_program(self, program: LoyaltyProgram) -> LoyaltyProgram:
        result = await self._session.execute(
            select(LoyaltyProgramModel).where(LoyaltyProgramModel.id == program.id)
        )
        model = result.scalar_one_or_none()
        if model:
            model.name = program.name
            model.program_type = program.program_type
            model.visits_required = program.visits_required
            model.points_per_visit = program.points_per_visit
            model.is_active = program.is_active
            await self._session.flush()
            return self._program_to_entity(model)
        return program

    # ── Cards ───────────────────────────────────────────

    async def get_card(self, user_id: UUID, business_id: UUID) -> LoyaltyCard | None:
        result = await self._session.execute(
            select(LoyaltyCardModel).where(
                LoyaltyCardModel.user_id == user_id,
                LoyaltyCardModel.business_id == business_id,
            )
        )
        model = result.scalar_one_or_none()
        return self._card_to_entity(model) if model else None

    async def create_card(self, card: LoyaltyCard) -> LoyaltyCard:
        model = LoyaltyCardModel(
            id=card.id, user_id=card.user_id, program_id=card.program_id,
            business_id=card.business_id, current_visits=card.current_visits,
            current_points=card.current_points, total_visits=card.total_visits,
            total_points=card.total_points, status=card.status,
        )
        self._session.add(model)
        await self._session.flush()
        return self._card_to_entity(model)

    async def update_card(self, card: LoyaltyCard) -> LoyaltyCard:
        result = await self._session.execute(
            select(LoyaltyCardModel).where(LoyaltyCardModel.id == card.id)
        )
        model = result.scalar_one_or_none()
        if model:
            model.current_visits = card.current_visits
            model.current_points = card.current_points
            model.total_visits = card.total_visits
            model.total_points = card.total_points
            model.status = card.status
            model.last_visit_at = card.last_visit_at
            await self._session.flush()
            return self._card_to_entity(model)
        return card

    async def get_user_cards(self, user_id: UUID) -> list[LoyaltyCard]:
        result = await self._session.execute(
            select(LoyaltyCardModel).where(LoyaltyCardModel.user_id == user_id)
        )
        return [self._card_to_entity(m) for m in result.scalars().all()]

    async def get_active_cards_count(self, business_id: UUID) -> int:
        result = await self._session.execute(
            select(func.count(LoyaltyCardModel.id)).where(
                LoyaltyCardModel.business_id == business_id,
                LoyaltyCardModel.status == "active",
            )
        )
        return result.scalar() or 0

    # ── Rewards ─────────────────────────────────────────

    async def create_reward(self, reward: Reward) -> Reward:
        model = RewardModel(
            id=reward.id, program_id=reward.program_id, business_id=reward.business_id,
            title=reward.title, description=reward.description, reward_type=reward.reward_type,
            value=reward.value, points_cost=reward.points_cost, visits_cost=reward.visits_cost,
            stock=reward.stock, is_active=reward.is_active,
        )
        self._session.add(model)
        await self._session.flush()
        return self._reward_to_entity(model)

    async def get_reward(self, reward_id: UUID) -> Reward | None:
        result = await self._session.execute(
            select(RewardModel).where(RewardModel.id == reward_id)
        )
        model = result.scalar_one_or_none()
        return self._reward_to_entity(model) if model else None

    async def get_rewards_by_program(self, program_id: UUID) -> list[Reward]:
        result = await self._session.execute(
            select(RewardModel).where(
                RewardModel.program_id == program_id,
                RewardModel.is_active == True,
            )
        )
        return [self._reward_to_entity(m) for m in result.scalars().all()]

    async def update_reward(self, reward: Reward) -> Reward:
        result = await self._session.execute(
            select(RewardModel).where(RewardModel.id == reward.id)
        )
        model = result.scalar_one_or_none()
        if model:
            model.stock = reward.stock
            model.is_active = reward.is_active
            await self._session.flush()
            return self._reward_to_entity(model)
        return reward

    # ── Redemptions ─────────────────────────────────────

    async def create_redemption(self, redemption: Redemption) -> Redemption:
        model = RedemptionModel(
            id=redemption.id, reward_id=redemption.reward_id, user_id=redemption.user_id,
            business_id=redemption.business_id, code=redemption.code, status=redemption.status,
            redeemed_at=redemption.redeemed_at, expires_at=redemption.expires_at,
        )
        self._session.add(model)
        await self._session.flush()
        return self._redemption_to_entity(model)

    async def get_redemption_by_code(self, code: str) -> Redemption | None:
        result = await self._session.execute(
            select(RedemptionModel).where(RedemptionModel.code == code)
        )
        model = result.scalar_one_or_none()
        return self._redemption_to_entity(model) if model else None

    async def get_redemptions_by_business(
        self, business_id: UUID, limit: int = 50, offset: int = 0
    ) -> list[Redemption]:
        result = await self._session.execute(
            select(RedemptionModel)
            .where(RedemptionModel.business_id == business_id)
            .order_by(RedemptionModel.redeemed_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return [self._redemption_to_entity(m) for m in result.scalars().all()]

    async def update_redemption(self, redemption: Redemption) -> Redemption:
        result = await self._session.execute(
            select(RedemptionModel).where(RedemptionModel.id == redemption.id)
        )
        model = result.scalar_one_or_none()
        if model:
            model.status = redemption.status
            model.used_at = redemption.used_at
            await self._session.flush()
            return self._redemption_to_entity(model)
        return redemption

    async def get_total_redeemed(self, business_id: UUID) -> int:
        result = await self._session.execute(
            select(func.count(RedemptionModel.id)).where(
                RedemptionModel.business_id == business_id,
            )
        )
        return result.scalar() or 0
