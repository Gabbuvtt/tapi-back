"""
Redis cache service for TAPI.

Handles:
- Business/menu/loyalty cache with TTL-based invalidation.
- Offline review queue for batch processing.
- Rate limiting support.
"""

import json
from typing import Any

import redis.asyncio as aioredis

from core.config import settings
from core.constants import (
    CACHE_TTL_BUSINESS,
    CACHE_TTL_LOYALTY_PROGRAM,
    CACHE_TTL_MENU,
    CACHE_TTL_METRICS,
)


# ── Global Redis Client ────────────────────────────────

_redis: aioredis.Redis | None = None


async def init_redis() -> None:
    """Initialize the Redis connection."""
    global _redis
    _redis = aioredis.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True,
    )
    # Verify connection
    await _redis.ping()


async def close_redis() -> None:
    """Close the Redis connection."""
    global _redis
    if _redis:
        await _redis.close()


def get_redis() -> aioredis.Redis:
    """Get the Redis client instance."""
    if _redis is None:
        raise RuntimeError("Redis is not initialized. Call init_redis() first.")
    return _redis


# ── Cache Service ───────────────────────────────────────

class RedisCache:
    """High-level cache operations with domain-specific key patterns."""

    def __init__(self, redis_client: aioredis.Redis):
        self._redis = redis_client

    # ── Generic Cache Operations ────────────────────────

    async def get(self, key: str) -> Any | None:
        """Get a cached value by key."""
        data = await self._redis.get(key)
        if data:
            return json.loads(data)
        return None

    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Set a cache value with optional TTL (seconds)."""
        serialized = json.dumps(value, default=str)
        if ttl:
            await self._redis.setex(key, ttl, serialized)
        else:
            await self._redis.set(key, serialized)

    async def delete(self, key: str) -> None:
        """Delete a cache key."""
        await self._redis.delete(key)

    async def delete_pattern(self, pattern: str) -> None:
        """Delete all keys matching a pattern."""
        keys = []
        async for key in self._redis.scan_iter(match=pattern):
            keys.append(key)
        if keys:
            await self._redis.delete(*keys)

    # ── Domain-Specific Cache ───────────────────────────

    async def get_business(self, slug: str) -> dict | None:
        """Get cached business data by slug."""
        return await self.get(f"business:{slug}")

    async def set_business(self, slug: str, data: dict) -> None:
        """Cache business data."""
        await self.set(f"business:{slug}", data, ttl=CACHE_TTL_BUSINESS)

    async def invalidate_business(self, slug: str) -> None:
        """Invalidate business cache."""
        await self.delete(f"business:{slug}")

    async def get_menu(self, business_id: str) -> dict | None:
        """Get cached menu data."""
        return await self.get(f"menu:{business_id}")

    async def set_menu(self, business_id: str, data: dict) -> None:
        """Cache menu data."""
        await self.set(f"menu:{business_id}", data, ttl=CACHE_TTL_MENU)

    async def invalidate_menu(self, business_id: str) -> None:
        """Invalidate menu cache."""
        await self.delete(f"menu:{business_id}")

    async def get_loyalty_program(self, business_id: str) -> dict | None:
        """Get cached loyalty program data."""
        return await self.get(f"loyalty_program:{business_id}")

    async def set_loyalty_program(self, business_id: str, data: dict) -> None:
        """Cache loyalty program data."""
        await self.set(
            f"loyalty_program:{business_id}", data, ttl=CACHE_TTL_LOYALTY_PROGRAM
        )

    async def invalidate_loyalty_program(self, business_id: str) -> None:
        """Invalidate loyalty program cache."""
        await self.delete(f"loyalty_program:{business_id}")

    # ── Offline Review Queue ────────────────────────────

    async def enqueue_offline_review(self, review_data: dict) -> None:
        """Push a review to the offline processing queue."""
        serialized = json.dumps(review_data, default=str)
        await self._redis.lpush("offline_review_queue", serialized)

    async def dequeue_offline_reviews(self, batch_size: int = 50) -> list[dict]:
        """Pop a batch of reviews from the offline queue."""
        reviews = []
        for _ in range(batch_size):
            data = await self._redis.rpop("offline_review_queue")
            if data is None:
                break
            reviews.append(json.loads(data))
        return reviews

    async def get_offline_queue_length(self) -> int:
        """Get the number of reviews in the offline queue."""
        return await self._redis.llen("offline_review_queue")

    # ── Rate Limiting ───────────────────────────────────

    async def check_rate_limit(
        self, key: str, max_requests: int, window_seconds: int
    ) -> bool:
        """
        Check if a request is within the rate limit.

        Args:
            key: Rate limit key (e.g., "rate:{ip}:{endpoint}").
            max_requests: Maximum requests allowed in the window.
            window_seconds: Time window in seconds.

        Returns:
            True if the request is allowed, False if rate limited.
        """
        current = await self._redis.incr(key)
        if current == 1:
            await self._redis.expire(key, window_seconds)
        return current <= max_requests
