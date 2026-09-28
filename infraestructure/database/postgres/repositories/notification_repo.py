"""
Notification repository — PostgreSQL implementation.
"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.notification import NotificationCampaign, NotificationLog
from domain.repositories.notification_repository import NotificationRepository
from infraestructure.database.postgres.models import (
    NotificationCampaignModel,
    NotificationLogModel,
)


class PostgresNotificationRepository(NotificationRepository):
    """Concrete notification repository backed by PostgreSQL."""

    def __init__(self, session: AsyncSession):
        self._session = session

    # ── Mappers ─────────────────────────────────────────

    @staticmethod
    def _campaign_to_entity(model: NotificationCampaignModel) -> NotificationCampaign:
        return NotificationCampaign(
            id=model.id, business_id=model.business_id, title=model.title,
            message=model.message, target_type=model.target_type,
            inactive_days=model.inactive_days, channel=model.channel,
            status=model.status, scheduled_at=model.scheduled_at,
            sent_at=model.sent_at, created_at=model.created_at,
        )

    @staticmethod
    def _log_to_entity(model: NotificationLogModel) -> NotificationLog:
        return NotificationLog(
            id=model.id, campaign_id=model.campaign_id, user_id=model.user_id,
            channel=model.channel, status=model.status, sent_at=model.sent_at,
        )

    # ── Campaigns ───────────────────────────────────────

    async def create_campaign(self, campaign: NotificationCampaign) -> NotificationCampaign:
        model = NotificationCampaignModel(
            id=campaign.id, business_id=campaign.business_id, title=campaign.title,
            message=campaign.message, target_type=campaign.target_type,
            inactive_days=campaign.inactive_days, channel=campaign.channel,
            status=campaign.status, scheduled_at=campaign.scheduled_at,
            sent_at=campaign.sent_at,
        )
        self._session.add(model)
        await self._session.flush()
        return self._campaign_to_entity(model)

    async def get_campaign(self, campaign_id: UUID) -> NotificationCampaign | None:
        result = await self._session.execute(
            select(NotificationCampaignModel).where(NotificationCampaignModel.id == campaign_id)
        )
        model = result.scalar_one_or_none()
        return self._campaign_to_entity(model) if model else None

    async def get_campaigns(self, business_id: UUID) -> list[NotificationCampaign]:
        result = await self._session.execute(
            select(NotificationCampaignModel)
            .where(NotificationCampaignModel.business_id == business_id)
            .order_by(NotificationCampaignModel.created_at.desc())
        )
        return [self._campaign_to_entity(m) for m in result.scalars().all()]

    async def update_campaign(self, campaign: NotificationCampaign) -> NotificationCampaign:
        result = await self._session.execute(
            select(NotificationCampaignModel).where(NotificationCampaignModel.id == campaign.id)
        )
        model = result.scalar_one_or_none()
        if model:
            model.status = campaign.status
            model.sent_at = campaign.sent_at
            await self._session.flush()
            return self._campaign_to_entity(model)
        return campaign

    # ── Logs ────────────────────────────────────────────

    async def create_log(self, log: NotificationLog) -> NotificationLog:
        model = NotificationLogModel(
            id=log.id, campaign_id=log.campaign_id, user_id=log.user_id,
            channel=log.channel, status=log.status, sent_at=log.sent_at,
        )
        self._session.add(model)
        await self._session.flush()
        return self._log_to_entity(model)

    async def get_campaign_logs(self, campaign_id: UUID) -> list[NotificationLog]:
        result = await self._session.execute(
            select(NotificationLogModel).where(NotificationLogModel.campaign_id == campaign_id)
        )
        return [self._log_to_entity(m) for m in result.scalars().all()]

    async def update_log_status(self, log_id: UUID, status: str) -> None:
        result = await self._session.execute(
            select(NotificationLogModel).where(NotificationLogModel.id == log_id)
        )
        model = result.scalar_one_or_none()
        if model:
            model.status = status
            await self._session.flush()
