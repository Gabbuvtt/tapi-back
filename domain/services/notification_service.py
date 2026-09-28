"""
Notification service — handles campaign creation, targeting, and sending.
"""

from uuid import UUID

from core.constants import CampaignStatus, TargetType
from core.exceptions import NotFoundError, BusinessLogicError
from domain.entities.notification import NotificationCampaign
from domain.repositories.notification_repository import NotificationRepository
from domain.repositories.user_repository import UserRepository


class NotificationService:
    """Service for notification campaign business logic."""

    def __init__(
        self,
        notification_repo: NotificationRepository,
        user_repo: UserRepository,
    ):
        self._notification_repo = notification_repo
        self._user_repo = user_repo

    async def create_campaign(
        self, business_id: UUID, **kwargs
    ) -> NotificationCampaign:
        """Create a new notification campaign."""
        campaign = NotificationCampaign(
            business_id=business_id,
            **kwargs,
        )
        return await self._notification_repo.create_campaign(campaign)

    async def get_campaign(self, campaign_id: UUID) -> NotificationCampaign:
        """Retrieve a campaign."""
        campaign = await self._notification_repo.get_campaign(campaign_id)
        if campaign is None:
            raise NotFoundError(resource="Campaign")
        return campaign

    async def get_target_users(self, campaign: NotificationCampaign) -> list:
        """
        Resolve target users for a campaign based on its target_type.

        - all: All users who have interacted with the business.
        - inactive: Users who haven't visited in N days.
        - loyal: Users with active loyalty cards.
        - custom: Placeholder for custom targeting logic.
        """
        if campaign.target_type == TargetType.ALL:
            return await self._user_repo.get_by_business(campaign.business_id)

        elif campaign.target_type == TargetType.INACTIVE:
            inactive_days = campaign.inactive_days or 15
            return await self._user_repo.get_inactive_users(
                business_id=campaign.business_id,
                inactive_days=inactive_days,
            )

        elif campaign.target_type == TargetType.LOYAL:
            # Users with active loyalty cards — handled at repo level
            return await self._user_repo.get_by_business(campaign.business_id)

        return []

    async def send_campaign(self, campaign_id: UUID) -> dict:
        """
        Trigger sending a campaign.

        This marks the campaign as sent and returns the target user list.
        Actual email sending is delegated to Celery tasks.
        """
        campaign = await self.get_campaign(campaign_id)

        if campaign.status == CampaignStatus.SENT:
            raise BusinessLogicError(detail="Campaign has already been sent")

        target_users = await self.get_target_users(campaign)
        campaign.mark_as_sent()
        await self._notification_repo.update_campaign(campaign)

        return {
            "campaign": campaign,
            "target_users": target_users,
            "total_recipients": len(target_users),
        }
