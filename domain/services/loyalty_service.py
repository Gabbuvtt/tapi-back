"""
Loyalty service — handles loyalty programs, card progression, and reward redemption.

Core flow:
1. Business creates a loyalty program with goals.
2. Each NFC scan auto-increments the user's loyalty card.
3. When goal is reached, rewards become available.
4. User redeems → gets a unique code to show at the store.
"""

from uuid import UUID

from core.constants import CardStatus
from core.exceptions import (
    BusinessLogicError,
    InsufficientPointsError,
    NotFoundError,
    RewardOutOfStockError,
)
from domain.entities.loyalty import LoyaltyCard, LoyaltyProgram
from domain.entities.reward import Redemption, Reward
from domain.repositories.loyalty_repository import LoyaltyRepository


class LoyaltyService:
    """Service for loyalty program business logic."""

    def __init__(self, loyalty_repo: LoyaltyRepository):
        self._loyalty_repo = loyalty_repo

    # ── Programs ────────────────────────────────────────

    async def create_program(
        self, business_id: UUID, name: str, program_type: str,
        visits_required: int = 10, points_per_visit: int = 1,
    ) -> LoyaltyProgram:
        """Create a new loyalty program for a business."""
        # Check if business already has an active program
        existing = await self._loyalty_repo.get_program_by_business(business_id)
        if existing and existing.is_active:
            raise BusinessLogicError(
                detail="Business already has an active loyalty program"
            )

        program = LoyaltyProgram(
            business_id=business_id,
            name=name,
            program_type=program_type,
            visits_required=visits_required,
            points_per_visit=points_per_visit,
        )
        return await self._loyalty_repo.create_program(program)

    async def get_program(self, program_id: UUID) -> LoyaltyProgram:
        """Retrieve a loyalty program."""
        program = await self._loyalty_repo.get_program(program_id)
        if program is None:
            raise NotFoundError(resource="Loyalty program")
        return program

    async def update_program(
        self, program_id: UUID, **kwargs
    ) -> LoyaltyProgram:
        """Update a loyalty program."""
        program = await self.get_program(program_id)
        for key, value in kwargs.items():
            if hasattr(program, key) and value is not None:
                setattr(program, key, value)
        return await self._loyalty_repo.update_program(program)

    # ── Cards ───────────────────────────────────────────

    async def register_visit(
        self, user_id: UUID, business_id: UUID
    ) -> dict:
        """
        Register a visit and update the user's loyalty card.

        Called automatically when an NFC scan is recorded.

        Returns:
            dict with card data and whether a reward was unlocked.
        """
        program = await self._loyalty_repo.get_program_by_business(business_id)
        if program is None or not program.is_active:
            return {"loyalty_active": False}

        # Get or create the user's card
        card = await self._loyalty_repo.get_card(user_id, business_id)
        if card is None:
            card = LoyaltyCard(
                user_id=user_id,
                program_id=program.id,
                business_id=business_id,
            )
            card = await self._loyalty_repo.create_card(card)

        # Register the visit
        card.register_visit(points_per_visit=program.points_per_visit)

        # Check if goal was reached
        reward_unlocked = card.check_completion(program.visits_required)

        card = await self._loyalty_repo.update_card(card)

        # Get available rewards
        rewards = await self._loyalty_repo.get_rewards_by_program(program.id)
        available_rewards = [r for r in rewards if r.is_available]

        return {
            "loyalty_active": True,
            "card": card,
            "program": program,
            "reward_unlocked": reward_unlocked,
            "available_rewards": available_rewards,
            "progress_pct": card.current_visits / program.visits_required,
            "message": self._build_message(card, program, reward_unlocked),
        }

    async def get_user_cards(self, user_id: UUID) -> list[LoyaltyCard]:
        """Get all loyalty cards for a user."""
        return await self._loyalty_repo.get_user_cards(user_id)

    # ── Rewards ─────────────────────────────────────────

    async def create_reward(
        self, program_id: UUID, business_id: UUID, **kwargs
    ) -> Reward:
        """Create a new reward for a loyalty program."""
        reward = Reward(
            program_id=program_id,
            business_id=business_id,
            **kwargs,
        )
        return await self._loyalty_repo.create_reward(reward)

    async def redeem_reward(
        self, user_id: UUID, reward_id: UUID
    ) -> Redemption:
        """
        Redeem a reward — generates a unique code for the customer.

        Validates:
        - Reward exists and is available
        - User has a completed loyalty card for the business
        """
        reward = await self._loyalty_repo.get_reward(reward_id)
        if reward is None:
            raise NotFoundError(resource="Reward")
        if not reward.is_available:
            raise RewardOutOfStockError()

        # Verify the user has a completed card
        card = await self._loyalty_repo.get_card(user_id, reward.business_id)
        if card is None or card.status != CardStatus.COMPLETED:
            raise InsufficientPointsError(
                detail="You need to complete your loyalty card to redeem this reward"
            )

        # Create redemption with unique code
        redemption = Redemption(
            reward_id=reward.id,
            user_id=user_id,
            business_id=reward.business_id,
        )

        # Decrement reward stock
        reward.decrement_stock()
        await self._loyalty_repo.update_reward(reward)

        # Reset card progress
        card.reset_progress()
        await self._loyalty_repo.update_card(card)

        return await self._loyalty_repo.create_redemption(redemption)

    # ── Helpers ─────────────────────────────────────────

    @staticmethod
    def _build_message(
        card: LoyaltyCard, program: LoyaltyProgram, reward_unlocked: bool
    ) -> str:
        """Build a user-friendly progress message."""
        if reward_unlocked:
            return "🎉 ¡Felicidades! Has desbloqueado una recompensa."
        remaining = program.visits_required - card.current_visits
        return (
            f"¡Bienvenido de nuevo! Visita {card.current_visits} de "
            f"{program.visits_required}. Te faltan {remaining} para tu premio."
        )
