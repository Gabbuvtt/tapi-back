"""
Review service — handles review creation, offline sync, and Google Maps routing.

Business rules:
- Reviews with rating >= 4 are queued for Google Maps submission.
- Reviews with rating < 4 stay internal for business insight.
- Offline reviews are bulk-inserted via the sync endpoint.
"""

from uuid import UUID

from core.constants import GOOGLE_REVIEW_MIN_RATING, ReviewStatus
from core.exceptions import NotFoundError, BusinessLogicError
from domain.entities.review import Review
from domain.repositories.review_repository import ReviewRepository


class ReviewService:
    """Service for review business logic."""

    def __init__(self, review_repo: ReviewRepository):
        self._review_repo = review_repo

    async def create_review(
        self,
        user_id: UUID,
        business_id: UUID,
        rating: int,
        comment: str | None = None,
        is_offline: bool = False,
        device_info: dict | None = None,
    ) -> Review:
        """
        Create a new review and route based on rating.

        Args:
            user_id: The reviewing user's ID.
            business_id: The business being reviewed.
            rating: Rating from 1-5.
            comment: Optional text comment.
            is_offline: Whether this review was cached offline.
            device_info: Optional device metadata.

        Returns:
            The created Review entity.

        Raises:
            BusinessLogicError: If rating is out of range.
        """
        if not 1 <= rating <= 5:
            raise BusinessLogicError(detail="Rating must be between 1 and 5")

        review = Review(
            user_id=user_id,
            business_id=business_id,
            rating=rating,
            comment=comment,
            is_offline=is_offline,
            device_info=device_info,
        )

        # Apply business rule: route based on rating
        if review.should_send_to_google:
            review.status = ReviewStatus.PENDING  # Will be picked up by Celery
        else:
            review.mark_as_approved()  # Stays internal

        review = await self._review_repo.create(review)
        return review

    async def sync_offline_reviews(
        self, user_id: UUID, reviews_data: list[dict]
    ) -> int:
        """
        Bulk-sync reviews that were cached offline.

        Args:
            user_id: The user who created the reviews.
            reviews_data: List of review dicts from the offline queue.

        Returns:
            Number of reviews queued for processing.
        """
        reviews = []
        for data in reviews_data:
            review = Review(
                user_id=user_id,
                business_id=data["business_id"],
                rating=data["rating"],
                comment=data.get("comment"),
                is_offline=True,
                source="offline_sync",
            )
            if review.should_send_to_google:
                review.status = ReviewStatus.PENDING
            else:
                review.mark_as_approved()
            reviews.append(review)

        inserted = await self._review_repo.bulk_create(reviews)
        return inserted

    async def get_business_reviews(
        self,
        business_id: UUID,
        limit: int = 20,
        offset: int = 0,
        status: str | None = None,
    ) -> list[Review]:
        """Retrieve reviews for a business."""
        return await self._review_repo.get_by_business(
            business_id=business_id,
            limit=limit,
            offset=offset,
            status=status,
        )

    async def get_review_stats(self, business_id: UUID) -> dict:
        """Get review statistics for the dashboard."""
        return await self._review_repo.get_stats(business_id)
