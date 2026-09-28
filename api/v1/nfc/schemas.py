"""
Pydantic schemas for the NFC module.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from api.v1.businesses.schemas import BusinessPublicResponse
from api.v1.loyalty.schemas import LoyaltyCardResponse


class NfcScanRequest(BaseModel):
    """Request to register an NFC scan."""
    tag_uid: str = Field(..., min_length=4, max_length=100, description="NFC tag hardware UID")


class NfcTagCreate(BaseModel):
    """Request to register a new NFC tag."""
    tag_uid: str = Field(..., min_length=4, max_length=100)
    business_id: UUID
    label: str = Field("", max_length=255)


class NfcTagResponse(BaseModel):
    """NFC tag response."""
    id: UUID
    tag_uid: str
    business_id: UUID
    label: str
    is_active: bool
    created_at: datetime


class NfcScanResponse(BaseModel):
    """Response after an NFC scan."""
    business: BusinessPublicResponse
    loyalty_card: LoyaltyCardResponse | None = None
    scan_count: int
    message: str
