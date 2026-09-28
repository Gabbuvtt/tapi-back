"""
Notification entity — domain representation of campaigns and logs.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4

from core.constants import CampaignStatus, NotificationChannel, NotificationLogStatus, TargetType


@dataclass
class NotificationCampaign:
    """
    A notification campaign created by a business.

    Targets can be: all customers, inactive customers, loyal customers,
    or a custom selection.
    """

    id: UUID = field(default_factory=uuid4)
    business_id: UUID = field(default_factory=uuid4)
    title: str = ""
    message: str = ""
    target_type: str = TargetType.ALL
    inactive_days: int | None = None
    channel: str = NotificationChannel.EMAIL
    status: str = CampaignStatus.DRAFT
    scheduled_at: datetime | None = None
    sent_at: datetime | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def mark_as_sent(self) -> None:
        """Mark the campaign as sent."""
        self.status = CampaignStatus.SENT
        self.sent_at = datetime.now(timezone.utc)


@dataclass
class NotificationLog:
    """
    Tracks individual notification delivery status.
    """

    id: UUID = field(default_factory=uuid4)
    campaign_id: UUID = field(default_factory=uuid4)
    user_id: UUID = field(default_factory=uuid4)
    channel: str = NotificationChannel.EMAIL
    status: str = NotificationLogStatus.SENT
    sent_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
