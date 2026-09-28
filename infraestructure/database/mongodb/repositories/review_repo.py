"""
Review repository — MongoDB implementation.

Uses Motor async driver for non-blocking MongoDB operations.
Includes aggregation pipelines for review statistics.
"""

from datetime import datetime, timezone
from uuid import UUID

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from core.constants import ReviewStatus
from domain.entities.review import Review
from domain.repositories.review_repository import ReviewRepository


class MongoReviewRepository(ReviewRepository):
    """Concrete review repository backed by MongoDB."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self._collection = db["reviews"]

    # ── Mappers ─────────────────────────────────────────

    @staticmethod
    def _to_document(review: Review) -> dict:
        """Convert domain entity to MongoDB document."""
        doc = {
            "user_id": str(review.user_id),
            "business_id": str(review.business_id),
            "rating": review.rating,
            "comment": review.comment,
            "source": review.source,
            "status": review.status,
            "google_review_id": review.google_review_id,
            "is_offline": review.is_offline,
            "device_info": review.device_info,
            "created_at": review.created_at,
            "updated_at": review.updated_at,
            "synced_at": review.synced_at,
        }
        return doc

    @staticmethod
    def _to_entity(doc: dict) -> Review:
        """Convert MongoDB document to domain entity."""
        return Review(
            id=str(doc["_id"]),
            user_id=UUID(doc["user_id"]),
            business_id=UUID(doc["business_id"]),
            rating=doc["rating"],
            comment=doc.get("comment"),
            source=doc.get("source", "nfc_scan"),
            status=doc.get("status", ReviewStatus.PENDING),
            google_review_id=doc.get("google_review_id"),
            is_offline=doc.get("is_offline", False),
            device_info=doc.get("device_info"),
            created_at=doc.get("created_at", datetime.now(timezone.utc)),
            updated_at=doc.get("updated_at", datetime.now(timezone.utc)),
            synced_at=doc.get("synced_at"),
        )

    # ── CRUD ────────────────────────────────────────────

    async def create(self, review: Review) -> Review:
        doc = self._to_document(review)
        result = await self._collection.insert_one(doc)
        review.id = str(result.inserted_id)
        return review

    async def get_by_id(self, review_id: str) -> Review | None:
        doc = await self._collection.find_one({"_id": ObjectId(review_id)})
        return self._to_entity(doc) if doc else None

    async def get_by_business(
        self, business_id: UUID, limit: int = 20, offset: int = 0,
        status: str | None = None,
    ) -> list[Review]:
        query: dict = {"business_id": str(business_id)}
        if status:
            query["status"] = status

        cursor = (
            self._collection.find(query)
            .sort("created_at", -1)
            .skip(offset)
            .limit(limit)
        )
        return [self._to_entity(doc) async for doc in cursor]

    async def get_stats(self, business_id: UUID) -> dict:
        """Aggregation pipeline for review statistics."""
        pipeline = [
            {"$match": {"business_id": str(business_id)}},
            {
                "$group": {
                    "_id": None,
                    "total": {"$sum": 1},
                    "avg_rating": {"$avg": "$rating"},
                    "sent_to_google_count": {
                        "$sum": {
                            "$cond": [
                                {"$eq": ["$status", ReviewStatus.SENT_TO_GOOGLE]},
                                1,
                                0,
                            ]
                        }
                    },
                }
            },
        ]
        result = await self._collection.aggregate(pipeline).to_list(1)
        if result:
            stats = result[0]
            stats.pop("_id", None)
            stats["avg_rating"] = round(stats.get("avg_rating", 0.0), 1)
            return stats
        return {"total": 0, "avg_rating": 0.0, "sent_to_google_count": 0}

    async def bulk_create(self, reviews: list[Review]) -> int:
        if not reviews:
            return 0
        docs = [self._to_document(r) for r in reviews]
        result = await self._collection.insert_many(docs)
        return len(result.inserted_ids)

    async def update_status(self, review_id: str, status: str) -> None:
        await self._collection.update_one(
            {"_id": ObjectId(review_id)},
            {
                "$set": {
                    "status": status,
                    "updated_at": datetime.now(timezone.utc),
                }
            },
        )

    async def get_pending_for_google(self, limit: int = 50) -> list[Review]:
        cursor = (
            self._collection.find({"status": ReviewStatus.PENDING, "rating": {"$gte": 4}})
            .sort("created_at", 1)
            .limit(limit)
        )
        return [self._to_entity(doc) async for doc in cursor]
