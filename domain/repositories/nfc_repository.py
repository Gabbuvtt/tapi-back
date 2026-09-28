"""
NFC repository interface.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from domain.entities.nfc_scan import NfcScan, NfcTag


class NfcRepository(ABC):
    """Abstract repository for NFC tags and scan events."""

    # ── Tags ────────────────────────────────────────────

    @abstractmethod
    async def create_tag(self, tag: NfcTag) -> NfcTag:
        """Register a new NFC tag."""
        ...

    @abstractmethod
    async def get_tag_by_uid(self, tag_uid: str) -> NfcTag | None:
        """Retrieve a tag by its hardware UID."""
        ...

    @abstractmethod
    async def get_tags_by_business(self, business_id: UUID) -> list[NfcTag]:
        """List all tags for a business."""
        ...

    @abstractmethod
    async def deactivate_tag(self, tag_id: UUID) -> None:
        """Deactivate an NFC tag."""
        ...

    # ── Scans ───────────────────────────────────────────

    @abstractmethod
    async def create_scan(self, scan: NfcScan) -> NfcScan:
        """Record a new scan event."""
        ...

    @abstractmethod
    async def get_scans_by_business(
        self,
        business_id: UUID,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[NfcScan]:
        """Retrieve scans for a business within a date range."""
        ...

    @abstractmethod
    async def count_scans(
        self,
        business_id: UUID,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> int:
        """Count total scans for a business."""
        ...

    @abstractmethod
    async def count_unique_users(
        self,
        business_id: UUID,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> int:
        """Count unique users who scanned at a business."""
        ...

    @abstractmethod
    async def get_user_scan_count(self, user_id: UUID, business_id: UUID) -> int:
        """Count total scans by a specific user at a business."""
        ...

    @abstractmethod
    async def get_scan_timeline(
        self, business_id: UUID, start_date: datetime, end_date: datetime
    ) -> list[dict]:
        """
        Get scan counts grouped by date.

        Returns:
            List of dicts: [{"date": "2026-09-01", "count": 42}, ...]
        """
        ...
