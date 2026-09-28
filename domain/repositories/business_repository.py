"""
Business repository interface.
"""

from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.business import Business, BusinessMember


class BusinessRepository(ABC):
    """Abstract repository for Business persistence operations."""

    @abstractmethod
    async def create(self, business: Business) -> Business:
        """Persist a new business."""
        ...

    @abstractmethod
    async def get_by_id(self, business_id: UUID) -> Business | None:
        """Retrieve a business by ID."""
        ...

    @abstractmethod
    async def get_by_slug(self, slug: str) -> Business | None:
        """Retrieve a business by its URL slug."""
        ...

    @abstractmethod
    async def update(self, business: Business) -> Business:
        """Update an existing business."""
        ...

    @abstractmethod
    async def get_by_owner(self, owner_id: UUID) -> list[Business]:
        """Retrieve all businesses owned by a user."""
        ...

    @abstractmethod
    async def add_member(self, member: BusinessMember) -> BusinessMember:
        """Add a member to a business."""
        ...

    @abstractmethod
    async def get_members(self, business_id: UUID) -> list[BusinessMember]:
        """Retrieve all members of a business."""
        ...

    @abstractmethod
    async def is_member(self, business_id: UUID, user_id: UUID) -> bool:
        """Check if a user is a member of a business."""
        ...
