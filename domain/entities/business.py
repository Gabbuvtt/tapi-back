"""
Business entity — domain representation of a registered business/store.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4
import re


def _slugify(text: str) -> str:
    """Generate a URL-safe slug from text."""
    slug = text.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug.strip("-")


@dataclass
class Business:
    """
    Represents a business/store registered in TAPI.

    Businesses are associated with NFC tags and can configure
    loyalty programs, menus, and notification campaigns.
    """

    id: UUID = field(default_factory=uuid4)
    name: str = ""
    slug: str = ""
    email: str = ""
    phone: str | None = None
    address: str = ""
    google_place_id: str | None = None
    logo_url: str | None = None
    category: str = ""
    is_active: bool = True
    owner_id: UUID | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self):
        if not self.slug and self.name:
            self.slug = _slugify(self.name)

    def update(self, **kwargs) -> None:
        """Update business fields."""
        allowed = {"name", "phone", "address", "google_place_id", "logo_url", "category"}
        for key, value in kwargs.items():
            if key in allowed and value is not None:
                setattr(self, key, value)
        if "name" in kwargs and kwargs["name"]:
            self.slug = _slugify(kwargs["name"])
        self.updated_at = datetime.now(timezone.utc)


@dataclass
class BusinessMember:
    """
    Represents a user's membership/role within a business.

    Supports roles: owner, admin, staff.
    """

    id: UUID = field(default_factory=uuid4)
    business_id: UUID = field(default_factory=uuid4)
    user_id: UUID = field(default_factory=uuid4)
    role: str = "staff"  # owner | admin | staff
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
