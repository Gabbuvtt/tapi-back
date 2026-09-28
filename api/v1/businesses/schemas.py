"""
Pydantic schemas for the Business module.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class BusinessCreateRequest(BaseModel):
    """Request body for creating a new business."""
    name: str = Field(..., min_length=2, max_length=255)
    email: str = Field(..., max_length=255)
    phone: str | None = Field(None, max_length=20)
    address: str = Field(..., min_length=5)
    google_place_id: str | None = None
    category: str = Field(..., min_length=2, max_length=100)
    logo_url: str | None = None


class BusinessUpdateRequest(BaseModel):
    """Request body for updating a business."""
    name: str | None = Field(None, min_length=2, max_length=255)
    phone: str | None = None
    address: str | None = None
    google_place_id: str | None = None
    category: str | None = None
    logo_url: str | None = None


class BusinessResponse(BaseModel):
    """Full business response (for owners)."""
    id: UUID
    name: str
    slug: str
    email: str
    phone: str | None = None
    address: str
    google_place_id: str | None = None
    logo_url: str | None = None
    category: str
    is_active: bool
    owner_id: UUID
    created_at: datetime
    updated_at: datetime


class BusinessPublicResponse(BaseModel):
    """Public business response (for NFC scan landing)."""
    id: UUID
    name: str
    slug: str
    logo_url: str | None = None
    category: str
    address: str
    google_place_id: str | None = None
