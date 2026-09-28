"""
User entity — domain representation of a user.

This is a pure domain object, decoupled from any ORM or framework.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4


@dataclass
class User:
    """
    Represents a user in the TAPI system.

    Users authenticate via Google OAuth and can be customers
    or business owners. A single user can have both roles.
    """

    id: UUID = field(default_factory=uuid4)
    email: str = ""
    full_name: str = ""
    google_id: str = ""
    avatar_url: str | None = None
    phone: str | None = None
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def update_profile(self, full_name: str | None = None, phone: str | None = None) -> None:
        """Update mutable profile fields."""
        if full_name is not None:
            self.full_name = full_name
        if phone is not None:
            self.phone = phone
        self.updated_at = datetime.now(timezone.utc)
