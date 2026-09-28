"""
Pydantic schemas for the Notifications module.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class CampaignCreate(BaseModel):
    """Request to create a notification campaign."""
    title: str = Field(..., min_length=2, max_length=255)
    message: str = Field(..., min_length=10, max_length=2000)
    target_type: str = Field("all", pattern="^(all|inactive|loyal|custom)$")
    inactive_days: int | None = Field(None, ge=1)
    channel: str = Field("email", pattern="^(email|push|both)$")
    scheduled_at: datetime | None = None


class CampaignResponse(BaseModel):
    """Notification campaign response."""
    id: UUID
    business_id: UUID
    title: str
    message: str
    target_type: str
    inactive_days: int | None
    channel: str
    status: str
    scheduled_at: datetime | None
    sent_at: datetime | None
    created_at: datetime


class CampaignStats(BaseModel):
    """Campaign delivery statistics."""
    total_sent: int
    total_delivered: int
    total_failed: int
    total_opened: int
