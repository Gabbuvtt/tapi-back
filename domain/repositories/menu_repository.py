"""
Menu repository interface (MongoDB).
"""

from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.menu import Menu


class MenuRepository(ABC):
    """Abstract repository for Menu persistence operations (MongoDB)."""

    @abstractmethod
    async def create(self, menu: Menu) -> Menu:
        """Create a new menu."""
        ...

    @abstractmethod
    async def get_by_business(self, business_id: UUID) -> Menu | None:
        """Retrieve the active menu for a business."""
        ...

    @abstractmethod
    async def update(self, menu: Menu) -> Menu:
        """Update a menu."""
        ...

    @abstractmethod
    async def delete(self, menu_id: str) -> None:
        """Delete a menu by its MongoDB ObjectId."""
        ...
