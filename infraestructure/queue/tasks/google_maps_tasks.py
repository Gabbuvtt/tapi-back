"""
Google Maps Celery tasks — handles pushing reviews to Google.

Since Google doesn't provide a public API to post reviews,
this task generates a Google Maps review link that can be
sent to the user via email/notification.
"""

import asyncio
import logging

from infraestructure.queue.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="infraestructure.queue.tasks.google_maps_tasks.push_pending_reviews")
def push_pending_reviews():
    """
    Process reviews pending for Google Maps.

    Since Google doesn't allow posting reviews via API,
    this task updates the review status and prepares
    the Google Maps deep link for the user.
    """
    asyncio.run(_push_pending_reviews_async())


async def _push_pending_reviews_async():
    """Async implementation of Google Maps review processing."""
    from infraestructure.database.mongodb.connection import init_mongodb, get_mongodb, close_mongodb
    from infraestructure.database.mongodb.repositories.review_repo import MongoReviewRepository
    from core.constants import ReviewStatus

    try:
        await init_mongodb()
        review_repo = MongoReviewRepository(get_mongodb())

        pending = await review_repo.get_pending_for_google(limit=50)
        if not pending:
            logger.info("No pending reviews for Google Maps")
            return

        logger.info(f"Processing {len(pending)} reviews for Google Maps redirect")

        for review in pending:
            # Mark as approved since we can't post directly to Google.
            # The frontend will show a "Leave this review on Google Maps" CTA
            # with a deep link to the business's Google Maps page.
            await review_repo.update_status(
                review.id, ReviewStatus.APPROVED
            )
            logger.info(
                f"Review {review.id} (rating={review.rating}) "
                f"marked as approved — Google redirect pending"
            )

        logger.info(f"Processed {len(pending)} reviews")

    except Exception as e:
        logger.error(f"Error processing Google Maps reviews: {e}")
        raise

    finally:
        await close_mongodb()


def build_google_maps_review_url(google_place_id: str) -> str:
    """
    Build a Google Maps review deep link.

    This URL opens Google Maps directly on the review form
    for the specified business.

    Args:
        google_place_id: The Google Place ID of the business.

    Returns:
        URL string that opens the Google Maps review form.
    """
    return (
        f"https://search.google.com/local/writereview"
        f"?placeid={google_place_id}"
    )
