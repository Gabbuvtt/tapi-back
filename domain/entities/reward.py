"""
Reward and Redemption entities — domain objects for the rewards system.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4
import secrets

from core.constants import RedemptionStatus, RewardType


@dataclass
class Reward:
    """
    A reward offered by a business within a loyalty program.

    Examples: 10% discount, free coffee, 2x1 burger.
    """

    id: UUID = field(default_factory=uuid4)
    program_id: UUID = field(default_factory=uuid4)
    business_id: UUID = field(default_factory=uuid4)
    title: str = ""
    description: str = ""
    reward_type: str = RewardType.DISCOUNT_PCT
    value: float = 0.0  # 10.0 for 10% or $10
    points_cost: int = 0
    visits_cost: int = 0
    stock: int = -1  # -1 = unlimited
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def is_available(self) -> bool:
        """Check if the reward is still available."""
        return self.is_active and (self.stock == -1 or self.stock > 0)

    def decrement_stock(self) -> None:
        """Decrease stock by 1 if not unlimited."""
        if self.stock > 0:
            self.stock -= 1


@dataclass
class Redemption:
    """
    Tracks a customer's redemption of a reward.

    Generates a unique code that the customer shows at the store.
    """

    id: UUID = field(default_factory=uuid4)
    reward_id: UUID = field(default_factory=uuid4)
    user_id: UUID = field(default_factory=uuid4)
    business_id: UUID = field(default_factory=uuid4)
    code: str = field(default_factory=lambda: secrets.token_urlsafe(8).upper())
    status: str = RedemptionStatus.PENDING
    redeemed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc) + timedelta(days=7)
    )
    used_at: datetime | None = None

    @property
    def is_expired(self) -> bool:
        """Check if the redemption code has expired."""
        return datetime.now(timezone.utc) > self.expires_at

    def mark_as_used(self) -> None:
        """Mark the redemption as used by the business."""
        self.status = RedemptionStatus.USED
        self.used_at = datetime.now(timezone.utc)
