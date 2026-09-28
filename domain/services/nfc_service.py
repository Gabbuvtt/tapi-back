"""
NFC service — handles NFC scan registration and loyalty integration.

When a customer scans an NFC tag:
1. Validate the tag → find the business.
2. Record the scan event.
3. Trigger loyalty card progression.
"""

from uuid import UUID

from core.exceptions import NotFoundError, BusinessLogicError
from domain.entities.nfc_scan import NfcScan
from domain.repositories.nfc_repository import NfcRepository
from domain.repositories.business_repository import BusinessRepository
from domain.services.loyalty_service import LoyaltyService


class NfcService:
    """Service for NFC scan business logic."""

    def __init__(
        self,
        nfc_repo: NfcRepository,
        business_repo: BusinessRepository,
        loyalty_service: LoyaltyService,
    ):
        self._nfc_repo = nfc_repo
        self._business_repo = business_repo
        self._loyalty_service = loyalty_service

    async def register_scan(
        self,
        tag_uid: str,
        user_id: UUID | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> dict:
        """
        Register an NFC scan event.

        Args:
            tag_uid: The NFC tag's hardware UID.
            user_id: The authenticated user (if any).
            ip_address: Client IP.
            user_agent: Client user agent string.

        Returns:
            dict with business info, loyalty status, and scan count.

        Raises:
            NotFoundError: If the tag doesn't exist.
            BusinessLogicError: If the tag is inactive.
        """
        # Step 1: Find the tag
        tag = await self._nfc_repo.get_tag_by_uid(tag_uid)
        if tag is None:
            raise NotFoundError(resource="NFC tag")
        if not tag.is_active:
            raise BusinessLogicError(detail="This NFC tag has been deactivated")

        # Step 2: Get the business
        business = await self._business_repo.get_by_id(tag.business_id)
        if business is None:
            raise NotFoundError(resource="Business")

        # Step 3: Record the scan
        scan = NfcScan(
            tag_id=tag.id,
            user_id=user_id,
            business_id=business.id,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        scan = await self._nfc_repo.create_scan(scan)

        # Step 4: Update loyalty card (if user is authenticated)
        loyalty_data = {"loyalty_active": False}
        if user_id:
            loyalty_data = await self._loyalty_service.register_visit(
                user_id=user_id,
                business_id=business.id,
            )

        # Step 5: Get total scan count for this user
        scan_count = 0
        if user_id:
            scan_count = await self._nfc_repo.get_user_scan_count(
                user_id=user_id,
                business_id=business.id,
            )

        return {
            "business": business,
            "loyalty": loyalty_data,
            "scan_count": scan_count,
        }
