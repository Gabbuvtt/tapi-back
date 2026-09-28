"""
Pydantic schemas for the Reviews module.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ReviewCreateRequest(BaseModel):
    """Request to create a review."""
    business_id: UUID
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5")
    comment: str | None = Field(None, max_length=2000)
    is_offline: bool = False


class OfflineReviewItem(BaseModel):
    """A single review from offline cache."""
    business_id: UUID
    rating: int = Field(..., ge=1, le=5)
    comment: str | None = None
    cached_at: datetime
    device_id: str


class ReviewSyncRequest(BaseModel):
    """Batch of offline reviews to sync."""
    reviews: list[OfflineReviewItem]


class ReviewResponse(BaseModel):
    """Review response."""
    id: str
    user_id: UUID
    business_id: UUID
    rating: int
    comment: str | None = None
    status: str
    created_at: datetime


class ReviewStatsResponse(BaseModel):
    """Review statistics for a business."""
    total: int
    avg_rating: float
    sent_to_google_count: int


class SyncResponse(BaseModel):
    """Response for offline sync."""
    queued: int
    message: str
