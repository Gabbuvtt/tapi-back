"""
Review Celery tasks — processes offline review queue.

Reads batches from the Redis offline queue and bulk-inserts
them into MongoDB.
"""

import asyncio
import logging

from infraestructure.queue.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="infraestructure.queue.tasks.review_tasks.process_offline_queue")
def process_offline_queue():
    """
    Process the offline review queue.

    Called periodically by Celery Beat (every hour).
    Reads reviews from Redis queue and inserts into MongoDB.
    """
    asyncio.run(_process_offline_queue_async())


async def _process_offline_queue_async():
    """Async implementation of offline queue processing."""
    from infraestructure.cache.redis_cache import init_redis, get_redis, close_redis, RedisCache
    from infraestructure.database.mongodb.connection import init_mongodb, get_mongodb, close_mongodb
    from infraestructure.database.mongodb.repositories.review_repo import MongoReviewRepository
    from domain.entities.review import Review
    from core.constants import ReviewStatus, GOOGLE_REVIEW_MIN_RATING

    try:
        await init_redis()
        await init_mongodb()

        cache = RedisCache(get_redis())
        review_repo = MongoReviewRepository(get_mongodb())

        queue_length = await cache.get_offline_queue_length()
        if queue_length == 0:
            logger.info("Offline review queue is empty")
            return

        logger.info(f"Processing {queue_length} offline reviews")

        # Process in batches
        batch_size = 50
        total_processed = 0

        while True:
            batch = await cache.dequeue_offline_reviews(batch_size)
            if not batch:
                break

            reviews = []
            for data in batch:
                from uuid import UUID
                review = Review(
                    user_id=UUID(data["user_id"]),
                    business_id=UUID(data["business_id"]),
                    rating=data["rating"],
                    comment=data.get("comment"),
                    is_offline=True,
                    source="offline_sync",
                )
                if review.rating >= GOOGLE_REVIEW_MIN_RATING:
                    review.status = ReviewStatus.PENDING
                else:
                    review.mark_as_approved()
                reviews.append(review)

            inserted = await review_repo.bulk_create(reviews)
            total_processed += inserted
            logger.info(f"Inserted {inserted} reviews (batch)")

        logger.info(f"Total offline reviews processed: {total_processed}")

    except Exception as e:
        logger.error(f"Error processing offline queue: {e}")
        raise

    finally:
        await close_redis()
        await close_mongodb()
