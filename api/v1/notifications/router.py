"""
Notifications API endpoints.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, Query, BackgroundTasks

from api.dependencies import get_current_user_id, get_notification_service
from api.v1.notifications.schemas import CampaignCreate, CampaignResponse, CampaignStats
from domain.services.notification_service import NotificationService

router = APIRouter()


@router.post(
    "/campaigns",
    response_model=CampaignResponse,
    status_code=201,
    summary="Create campaign",
    description="Create a notification campaign for customers.",
)
async def create_campaign(
    request: CampaignCreate,
    business_id: UUID = Query(..., description="Business ID"),
    user_id: UUID = Depends(get_current_user_id),
    notification_service: NotificationService = Depends(get_notification_service),
):
    campaign = await notification_service.create_campaign(
        business_id=business_id,
        title=request.title,
        message=request.message,
        target_type=request.target_type,
        inactive_days=request.inactive_days,
        channel=request.channel,
        scheduled_at=request.scheduled_at,
    )
    return CampaignResponse(
        id=campaign.id, business_id=campaign.business_id, title=campaign.title,
        message=campaign.message, target_type=campaign.target_type,
        inactive_days=campaign.inactive_days, channel=campaign.channel,
        status=campaign.status, scheduled_at=campaign.scheduled_at,
        sent_at=campaign.sent_at, created_at=campaign.created_at,
    )


@router.get(
    "/campaigns",
    response_model=list[CampaignResponse],
    summary="List campaigns",
)
async def list_campaigns(
    business_id: UUID = Query(..., description="Business ID"),
    user_id: UUID = Depends(get_current_user_id),
    notification_service: NotificationService = Depends(get_notification_service),
):
    campaigns = await notification_service._notification_repo.get_campaigns(business_id)
    return [
        CampaignResponse(
            id=c.id, business_id=c.business_id, title=c.title,
            message=c.message, target_type=c.target_type,
            inactive_days=c.inactive_days, channel=c.channel,
            status=c.status, scheduled_at=c.scheduled_at,
            sent_at=c.sent_at, created_at=c.created_at,
        ) for c in campaigns
    ]


@router.post(
    "/campaigns/{campaign_id}/send",
    summary="Send campaign",
    description="Trigger campaign delivery asynchronously.",
)
async def send_campaign(
    campaign_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    notification_service: NotificationService = Depends(get_notification_service),
):
    await notification_service.send_campaign(campaign_id)
    return {"message": "Campaign queued for delivery"}


@router.get(
    "/campaigns/{campaign_id}/stats",
    response_model=CampaignStats,
    summary="Campaign stats",
)
async def campaign_stats(
    campaign_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    notification_service: NotificationService = Depends(get_notification_service),
):
    logs = await notification_service._notification_repo.get_campaign_logs(campaign_id)
    stats = {"total_sent": 0, "total_delivered": 0, "total_failed": 0, "total_opened": 0}
    for log in logs:
        if log.status == "sent": stats["total_sent"] += 1
        elif log.status == "delivered": stats["total_delivered"] += 1
        elif log.status == "failed": stats["total_failed"] += 1
        elif log.status == "opened": stats["total_opened"] += 1
    
    return CampaignStats(**stats)
