"""
Loyalty repository interface.
"""

from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.loyalty import LoyaltyCard, LoyaltyProgram
from domain.entities.reward import Redemption, Reward


class LoyaltyRepository(ABC):
    """Abstract repository for Loyalty persistence operations."""

    # ── Programs ────────────────────────────────────────

    @abstractmethod
    async def create_program(self, program: LoyaltyProgram) -> LoyaltyProgram:
        """Create a new loyalty program."""
        ...

    @abstractmethod
    async def get_program(self, program_id: UUID) -> LoyaltyProgram | None:
        """Retrieve a loyalty program by ID."""
        ...

    @abstractmethod
    async def get_program_by_business(self, business_id: UUID) -> LoyaltyProgram | None:
        """Retrieve the active loyalty program for a business."""
        ...

    @abstractmethod
    async def update_program(self, program: LoyaltyProgram) -> LoyaltyProgram:
        """Update a loyalty program."""
        ...

    # ── Cards ───────────────────────────────────────────

    @abstractmethod
    async def get_card(
        self, user_id: UUID, business_id: UUID
    ) -> LoyaltyCard | None:
        """Get a user's loyalty card for a specific business."""
        ...

    @abstractmethod
    async def create_card(self, card: LoyaltyCard) -> LoyaltyCard:
        """Create a new loyalty card."""
        ...

    @abstractmethod
    async def update_card(self, card: LoyaltyCard) -> LoyaltyCard:
        """Update a loyalty card (visits, points, status)."""
        ...

    @abstractmethod
    async def get_user_cards(self, user_id: UUID) -> list[LoyaltyCard]:
        """Get all loyalty cards for a user."""
        ...

    @abstractmethod
    async def get_active_cards_count(self, business_id: UUID) -> int:
        """Count active loyalty cards for a business."""
        ...

    # ── Rewards ─────────────────────────────────────────

    @abstractmethod
    async def create_reward(self, reward: Reward) -> Reward:
        """Create a new reward."""
        ...

    @abstractmethod
    async def get_reward(self, reward_id: UUID) -> Reward | None:
        """Retrieve a reward by ID."""
        ...

    @abstractmethod
    async def get_rewards_by_program(self, program_id: UUID) -> list[Reward]:
        """List all rewards for a loyalty program."""
        ...

    @abstractmethod
    async def update_reward(self, reward: Reward) -> Reward:
        """Update a reward."""
        ...

    # ── Redemptions ─────────────────────────────────────

    @abstractmethod
    async def create_redemption(self, redemption: Redemption) -> Redemption:
        """Create a new redemption record."""
        ...

    @abstractmethod
    async def get_redemption_by_code(self, code: str) -> Redemption | None:
        """Retrieve a redemption by its unique code."""
        ...

    @abstractmethod
    async def get_redemptions_by_business(
        self, business_id: UUID, limit: int = 50, offset: int = 0
    ) -> list[Redemption]:
        """List redemptions for a business."""
        ...

    @abstractmethod
    async def update_redemption(self, redemption: Redemption) -> Redemption:
        """Update a redemption status."""
        ...

    @abstractmethod
    async def get_total_redeemed(self, business_id: UUID) -> int:
        """Count total redemptions for a business."""
        ...
