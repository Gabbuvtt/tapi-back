"""
Notification repository interface.
"""

from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.notification import NotificationCampaign, NotificationLog


class NotificationRepository(ABC):
    """Abstract repository for notification campaigns and logs."""

    @abstractmethod
    async def create_campaign(
        self, campaign: NotificationCampaign
    ) -> NotificationCampaign:
        """Create a new notification campaign."""
        ...

    @abstractmethod
    async def get_campaign(self, campaign_id: UUID) -> NotificationCampaign | None:
        """Retrieve a campaign by ID."""
        ...

    @abstractmethod
    async def get_campaigns_by_business(
        self, business_id: UUID, limit: int = 20, offset: int = 0
    ) -> list[NotificationCampaign]:
        """List campaigns for a business."""
        ...

    @abstractmethod
    async def update_campaign(
        self, campaign: NotificationCampaign
    ) -> NotificationCampaign:
        """Update a campaign."""
        ...

    @abstractmethod
    async def create_log(self, log: NotificationLog) -> NotificationLog:
        """Create a notification delivery log entry."""
        ...

    @abstractmethod
    async def get_campaign_stats(self, campaign_id: UUID) -> dict:
        """
        Get delivery stats for a campaign.

        Returns:
            dict with keys: total_sent, delivered, failed, opened
        """
        ...
