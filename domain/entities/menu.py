"""
Menu entity — domain representation of a digital menu.

Stored in MongoDB for flexible, nested document structure.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID


@dataclass
class MenuItem:
    """A single item within a menu category."""

    name: str = ""
    description: str = ""
    price: float = 0.0
    currency: str = "USD"
    image_url: str | None = None
    is_available: bool = True
    tags: list[str] = field(default_factory=list)


@dataclass
class MenuCategory:
    """A category grouping within a menu (e.g., Burgers, Drinks)."""

    name: str = ""
    order: int = 0
    items: list[MenuItem] = field(default_factory=list)


@dataclass
class Menu:
    """
    A business's digital menu.

    Supports multiple categories with ordered items.
    """

    id: str | None = None  # MongoDB ObjectId as string
    business_id: UUID | None = None
    name: str = "Menú Principal"
    is_active: bool = True
    categories: list[MenuCategory] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
