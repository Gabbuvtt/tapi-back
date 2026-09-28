"""
Pydantic schemas for the Loyalty module.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


# ── Program Schemas ─────────────────────────────────────

class LoyaltyProgramCreate(BaseModel):
    """Request to create a loyalty program."""
    name: str = Field(..., min_length=2, max_length=255)
    program_type: str = Field(..., pattern="^(visits|points|hybrid)$")
    visits_required: int = Field(10, ge=1, le=100)
    points_per_visit: int = Field(1, ge=1, le=100)


class LoyaltyProgramUpdate(BaseModel):
    """Request to update a loyalty program."""
    name: str | None = None
    visits_required: int | None = Field(None, ge=1, le=100)
    points_per_visit: int | None = Field(None, ge=1, le=100)
    is_active: bool | None = None


class LoyaltyProgramResponse(BaseModel):
    """Loyalty program response."""
    id: UUID
    business_id: UUID
    name: str
    program_type: str
    visits_required: int
    points_per_visit: int
    is_active: bool
    created_at: datetime


# ── Card Schemas ────────────────────────────────────────

class LoyaltyCardResponse(BaseModel):
    """Loyalty card (customer progress) response."""
    id: UUID
    program_id: UUID
    business_id: UUID
    current_visits: int
    current_points: int
    total_visits: int
    total_points: int
    status: str
    progress_pct: float
    last_visit_at: datetime | None = None
    created_at: datetime


# ── Reward Schemas ──────────────────────────────────────

class RewardCreate(BaseModel):
    """Request to create a reward."""
    program_id: UUID
    title: str = Field(..., min_length=2, max_length=255)
    description: str = Field("", max_length=1000)
    reward_type: str = Field(..., pattern="^(discount_pct|discount_fixed|free_item|custom)$")
    value: float = Field(0.0, ge=0)
    points_cost: int = Field(0, ge=0)
    visits_cost: int = Field(0, ge=0)
    stock: int = Field(-1, ge=-1)


class RewardResponse(BaseModel):
    """Reward response."""
    id: UUID
    program_id: UUID
    business_id: UUID
    title: str
    description: str
    reward_type: str
    value: float
    points_cost: int
    visits_cost: int
    stock: int
    is_active: bool


# ── Redemption Schemas ──────────────────────────────────

class RedeemRequest(BaseModel):
    """Request to redeem a reward."""
    reward_id: UUID


class RedemptionResponse(BaseModel):
    """Redemption response with unique code."""
    id: UUID
    reward_id: UUID
    code: str
    status: str
    redeemed_at: datetime
    expires_at: datetime
