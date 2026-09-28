"""
NFC scan entity — domain representation of an NFC tag scan event.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4


@dataclass
class NfcTag:
    """
    Represents a physical NFC tag assigned to a business.

    Each tag has a unique UID and is linked to a specific business.
    """

    id: UUID = field(default_factory=uuid4)
    tag_uid: str = ""
    business_id: UUID = field(default_factory=uuid4)
    label: str = ""
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class NfcScan:
    """
    Records a single NFC scan event.

    Created every time a customer taps their phone on a business's
    NFC tag. Used for metrics and triggering loyalty points.
    """

    id: UUID = field(default_factory=uuid4)
    tag_id: UUID = field(default_factory=uuid4)
    user_id: UUID | None = None
    business_id: UUID = field(default_factory=uuid4)
    scanned_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    ip_address: str | None = None
    user_agent: str | None = None
