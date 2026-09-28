"""
Review repository interface — abstract contract for review persistence (MongoDB).
"""

from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from domain.entities.review import Review


class ReviewRepository(ABC):
    """Abstract repository for Review persistence operations (MongoDB)."""

    @abstractmethod
    async def create(self, review: Review) -> Review:
        """Persist a new review."""
        ...

    @abstractmethod
    async def get_by_id(self, review_id: str) -> Review | None:
        """Retrieve a review by its MongoDB ObjectId."""
        ...

    @abstractmethod
    async def get_by_business(
        self,
        business_id: UUID,
        limit: int = 20,
        offset: int = 0,
        status: str | None = None,
    ) -> list[Review]:
        """Retrieve reviews for a business with optional status filter."""
        ...

    @abstractmethod
    async def get_stats(self, business_id: UUID) -> dict:
        """
        Get review statistics for a business.

        Returns:
            dict with keys: total, avg_rating, rating_distribution,
            sent_to_google_count
        """
        ...

    @abstractmethod
    async def bulk_create(self, reviews: list[Review]) -> int:
        """
        Insert multiple reviews at once (for offline sync).

        Returns:
            Number of reviews inserted.
        """
        ...

    @abstractmethod
    async def update_status(self, review_id: str, status: str) -> None:
        """Update the status of a review."""
        ...

    @abstractmethod
    async def get_pending_for_google(self, limit: int = 50) -> list[Review]:
        """Get reviews pending to be sent to Google Maps."""
        ...
