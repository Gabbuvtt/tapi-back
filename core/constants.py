"""
Application-wide constants and enumerations.

Centralized here to avoid magic strings scattered across the codebase.
"""

from enum import StrEnum


# ── User Roles ──────────────────────────────────────────

class UserRole(StrEnum):
    CUSTOMER = "customer"
    BUSINESS_OWNER = "business_owner"
    ADMIN = "admin"


# ── Business Member Roles ──────────────────────────────

class MemberRole(StrEnum):
    OWNER = "owner"
    ADMIN = "admin"
    STAFF = "staff"


# ── Loyalty Program Types ──────────────────────────────

class ProgramType(StrEnum):
    VISITS = "visits"
    POINTS = "points"
    HYBRID = "hybrid"


# ── Loyalty Card Status ────────────────────────────────

class CardStatus(StrEnum):
    ACTIVE = "active"
    COMPLETED = "completed"
    EXPIRED = "expired"


# ── Reward Types ───────────────────────────────────────

class RewardType(StrEnum):
    DISCOUNT_PCT = "discount_pct"
    DISCOUNT_FIXED = "discount_fixed"
    FREE_ITEM = "free_item"
    CUSTOM = "custom"


# ── Redemption Status ─────────────────────────────────

class RedemptionStatus(StrEnum):
    PENDING = "pending"
    USED = "used"
    EXPIRED = "expired"


# ── Review Status ──────────────────────────────────────

class ReviewStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    SENT_TO_GOOGLE = "sent_to_google"
    REJECTED = "rejected"


# ── Notification Targets ──────────────────────────────

class TargetType(StrEnum):
    ALL = "all"
    INACTIVE = "inactive"
    LOYAL = "loyal"
    CUSTOM = "custom"


class NotificationChannel(StrEnum):
    EMAIL = "email"
    PUSH = "push"
    BOTH = "both"


class CampaignStatus(StrEnum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    SENT = "sent"


class NotificationLogStatus(StrEnum):
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    OPENED = "opened"


# ── Review Rating Threshold ───────────────────────────

GOOGLE_REVIEW_MIN_RATING = 4  # Reviews with rating >= 4 go to Google Maps


# ── Cache TTLs (seconds) ──────────────────────────────

CACHE_TTL_BUSINESS = 300       # 5 minutes
CACHE_TTL_MENU = 600           # 10 minutes
CACHE_TTL_LOYALTY_PROGRAM = 300  # 5 minutes
CACHE_TTL_METRICS = 120        # 2 minutes
