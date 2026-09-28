"""
Loyalty entities — LoyaltyProgram, LoyaltyCard for the fidelity system.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4

from core.constants import CardStatus, ProgramType


@dataclass
class LoyaltyProgram:
    """
    A loyalty program defined by a business.

    Types:
    - visits: Customer earns a reward after N visits.
    - points: Customer earns points per visit, redeems when threshold is met.
    - hybrid: Both visit count and point accumulation.
    """

    id: UUID = field(default_factory=uuid4)
    business_id: UUID = field(default_factory=uuid4)
    name: str = ""
    program_type: str = ProgramType.VISITS
    visits_required: int = 10
    points_per_visit: int = 1
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class LoyaltyCard:
    """
    A customer's loyalty card for a specific business program.

    Tracks visits and points accumulated. Status transitions:
    active → completed (when goal is reached) → active (after redemption/reset).
    """

    id: UUID = field(default_factory=uuid4)
    user_id: UUID = field(default_factory=uuid4)
    program_id: UUID = field(default_factory=uuid4)
    business_id: UUID = field(default_factory=uuid4)
    current_visits: int = 0
    current_points: int = 0
    total_visits: int = 0
    total_points: int = 0
    status: str = CardStatus.ACTIVE
    last_visit_at: datetime | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def register_visit(self, points_per_visit: int = 1) -> None:
        """Register a new visit, incrementing counters."""
        self.current_visits += 1
        self.total_visits += 1
        self.current_points += points_per_visit
        self.total_points += points_per_visit
        self.last_visit_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)

    def check_completion(self, visits_required: int) -> bool:
        """Check if the card has reached the program goal."""
        if self.current_visits >= visits_required:
            self.status = CardStatus.COMPLETED
            self.updated_at = datetime.now(timezone.utc)
            return True
        return False

    def reset_progress(self) -> None:
        """Reset current progress after reward redemption."""
        self.current_visits = 0
        self.current_points = 0
        self.status = CardStatus.ACTIVE
        self.updated_at = datetime.now(timezone.utc)

    @property
    def progress_pct(self) -> float:
        """Calculate progress percentage towards the visits goal."""
        # This needs visits_required from the program, handled at service level
        return 0.0
