"""
Pydantic schemas for the Menu module.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class MenuItemSchema(BaseModel):
    """A single item in a menu category."""
    name: str = Field(..., min_length=1, max_length=255)
    description: str = ""
    price: float = Field(..., ge=0)
    currency: str = Field("USD", max_length=3)
    image_url: str | None = None
    is_available: bool = True
    tags: list[str] = []


class MenuCategorySchema(BaseModel):
    """A category within a menu."""
    name: str = Field(..., min_length=1, max_length=255)
    order: int = 0
    items: list[MenuItemSchema] = []


class MenuCreateRequest(BaseModel):
    """Request to create a menu."""
    business_id: UUID
    name: str = Field("Menú Principal", min_length=1, max_length=255)
    categories: list[MenuCategorySchema] = []


class MenuUpdateRequest(BaseModel):
    """Request to update a menu."""
    name: str | None = None
    categories: list[MenuCategorySchema] | None = None


class MenuResponse(BaseModel):
    """Menu response with nested categories and items."""
    id: str
    business_id: UUID
    name: str
    is_active: bool
    categories: list[MenuCategorySchema]
    created_at: datetime
    updated_at: datetime
