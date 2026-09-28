"""
MongoDB async connection management using Motor.

Provides:
- Async MongoDB client and database.
- Collection accessors.
- Startup/shutdown lifecycle hooks.
"""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from core.config import settings


# ── Global Client ───────────────────────────────────────

_client: AsyncIOMotorClient | None = None
_database: AsyncIOMotorDatabase | None = None


async def init_mongodb() -> None:
    """Initialize the MongoDB connection."""
    global _client, _database
    _client = AsyncIOMotorClient(settings.MONGO_URL)
    _database = _client[settings.MONGO_DB]

    # Create indexes for performance
    reviews = _database["reviews"]
    await reviews.create_index("business_id")
    await reviews.create_index("user_id")
    await reviews.create_index("status")
    await reviews.create_index([("business_id", 1), ("created_at", -1)])

    menus = _database["menus"]
    await menus.create_index("business_id", unique=True)

    offline_queue = _database["offline_review_queue"]
    await offline_queue.create_index("status")


async def close_mongodb() -> None:
    """Close the MongoDB connection."""
    global _client
    if _client:
        _client.close()


def get_mongodb() -> AsyncIOMotorDatabase:
    """
    Get the MongoDB database instance.

    Usage in FastAPI dependency injection:
        db = get_mongodb()
        collection = db["reviews"]
    """
    if _database is None:
        raise RuntimeError("MongoDB is not initialized. Call init_mongodb() first.")
    return _database
