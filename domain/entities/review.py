"""
Review entity — domain representation of a customer review.

Reviews are stored in MongoDB. Positive reviews (rating >= 4) are
routed to Google Maps; lower ratings stay internal for business insight.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID

from core.constants import ReviewStatus, GOOGLE_REVIEW_MIN_RATING


@dataclass
class Review:
    """
    Represents a customer review for a business.

    Domain rule: if rating >= GOOGLE_REVIEW_MIN_RATING,
    the review should be forwarded to Google Maps.
    """

    id: str | None = None  # MongoDB ObjectId as string
    user_id: UUID | None = None
    business_id: UUID | None = None
    rating: int = 0
    comment: str | None = None
    source: str = "nfc_scan"
    status: str = ReviewStatus.PENDING
    google_review_id: str | None = None
    is_offline: bool = False
    device_info: dict | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    synced_at: datetime | None = None

    @property
    def should_send_to_google(self) -> bool:
        """Check if this review qualifies for Google Maps submission."""
        return self.rating >= GOOGLE_REVIEW_MIN_RATING

    def mark_as_approved(self) -> None:
        """Mark the review as approved (internal only)."""
        self.status = ReviewStatus.APPROVED
        self.updated_at = datetime.now(timezone.utc)

    def mark_as_sent_to_google(self, google_id: str) -> None:
        """Mark the review as sent to Google Maps."""
        self.status = ReviewStatus.SENT_TO_GOOGLE
        self.google_review_id = google_id
        self.updated_at = datetime.now(timezone.utc)
