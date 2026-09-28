"""
User repository interface — abstract contract for user persistence.

The domain layer depends on this interface; the infrastructure layer
provides the concrete implementation (PostgreSQL).
"""

from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.user import User


class UserRepository(ABC):
    """Abstract repository for User persistence operations."""

    @abstractmethod
    async def create(self, user: User) -> User:
        """Persist a new user."""
        ...

    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> User | None:
        """Retrieve a user by their ID."""
        ...

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        """Retrieve a user by their email."""
        ...

    @abstractmethod
    async def get_by_google_id(self, google_id: str) -> User | None:
        """Retrieve a user by their Google ID."""
        ...

    @abstractmethod
    async def update(self, user: User) -> User:
        """Update an existing user."""
        ...

    @abstractmethod
    async def get_by_business(
        self, business_id: UUID, limit: int = 50, offset: int = 0
    ) -> list[User]:
        """Retrieve users who have interacted with a business."""
        ...

    @abstractmethod
    async def get_inactive_users(
        self, business_id: UUID, inactive_days: int
    ) -> list[User]:
        """Retrieve users who haven't visited a business in N days."""
        ...
