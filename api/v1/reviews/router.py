"""
Reviews API endpoints.

POST /reviews           — Create a review
POST /reviews/sync      — Sync offline reviews (batch)
GET  /reviews           — List reviews for a business
GET  /reviews/stats     — Review statistics
"""

from uuid import UUID

from fastapi import APIRouter, Depends, Query

from api.dependencies import get_cache, get_current_user_id, get_review_service
from api.v1.reviews.schemas import (
    ReviewCreateRequest,
    ReviewResponse,
    ReviewStatsResponse,
    ReviewSyncRequest,
    SyncResponse,
)
from domain.services.review_service import ReviewService
from infraestructure.cache.redis_cache import RedisCache

router = APIRouter()


@router.post(
    "",
    response_model=ReviewResponse,
    status_code=201,
    summary="Create a review",
    description=(
        "Submit a review for a business. Reviews with rating >= 4 are queued "
        "for Google Maps redirect. Reviews with rating < 4 stay internal."
    ),
)
async def create_review(
    request: ReviewCreateRequest,
    user_id: UUID = Depends(get_current_user_id),
    review_service: ReviewService = Depends(get_review_service),
):
    review = await review_service.create_review(
        user_id=user_id,
        business_id=request.business_id,
        rating=request.rating,
        comment=request.comment,
        is_offline=request.is_offline,
    )
    return ReviewResponse(
        id=review.id,
        user_id=review.user_id,
        business_id=review.business_id,
        rating=review.rating,
        comment=review.comment,
        status=review.status,
        created_at=review.created_at,
    )


@router.post(
    "/sync",
    response_model=SyncResponse,
    status_code=202,
    summary="Sync offline reviews",
    description=(
        "Upload a batch of reviews that were cached offline. "
        "They are enqueued in Redis and processed by Celery workers."
    ),
)
async def sync_offline_reviews(
    request: ReviewSyncRequest,
    user_id: UUID = Depends(get_current_user_id),
    cache: RedisCache = Depends(get_cache),
):
    # Enqueue each review in Redis for async processing
    for review in request.reviews:
        await cache.enqueue_offline_review({
            "user_id": str(user_id),
            "business_id": str(review.business_id),
            "rating": review.rating,
            "comment": review.comment,
            "cached_at": str(review.cached_at),
            "device_id": review.device_id,
        })

    return SyncResponse(
        queued=len(request.reviews),
        message=f"{len(request.reviews)} reviews queued for processing",
    )


@router.get(
    "",
    response_model=list[ReviewResponse],
    summary="List reviews",
    description="Retrieve reviews for a specific business.",
)
async def list_reviews(
    business_id: UUID = Query(..., description="Business ID to filter by"),
    status: str | None = Query(None, description="Filter by status"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    review_service: ReviewService = Depends(get_review_service),
):
    reviews = await review_service.get_business_reviews(
        business_id=business_id,
        limit=limit,
        offset=offset,
        status=status,
    )
    return [
        ReviewResponse(
            id=r.id,
            user_id=r.user_id,
            business_id=r.business_id,
            rating=r.rating,
            comment=r.comment,
            status=r.status,
            created_at=r.created_at,
        )
        for r in reviews
    ]


@router.get(
    "/stats",
    response_model=ReviewStatsResponse,
    summary="Review statistics",
    description="Get review statistics for a business (total, avg rating, Google count).",
)
async def get_review_stats(
    business_id: UUID = Query(..., description="Business ID"),
    review_service: ReviewService = Depends(get_review_service),
):
    stats = await review_service.get_review_stats(business_id)
    return ReviewStatsResponse(**stats)
