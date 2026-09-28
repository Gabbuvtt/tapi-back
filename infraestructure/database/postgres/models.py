"""
SQLAlchemy ORM models for PostgreSQL.

These map domain entities to database tables. The domain layer
uses pure dataclasses; these models are for persistence only.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infraestructure.database.postgres.connection import Base


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


# ── Users ───────────────────────────────────────────────

class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    google_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utc_now, onupdate=_utc_now
    )

    # Relationships
    memberships: Mapped[list["BusinessMemberModel"]] = relationship(back_populates="user")
    scans: Mapped[list["NfcScanModel"]] = relationship(back_populates="user")
    loyalty_cards: Mapped[list["LoyaltyCardModel"]] = relationship(back_populates="user")
    redemptions: Mapped[list["RedemptionModel"]] = relationship(back_populates="user")


# ── Businesses ──────────────────────────────────────────

class BusinessModel(Base):
    __tablename__ = "businesses"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    address: Mapped[str] = mapped_column(Text, nullable=False)
    google_place_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    logo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utc_now, onupdate=_utc_now
    )

    # Relationships
    owner: Mapped["UserModel"] = relationship()
    members: Mapped[list["BusinessMemberModel"]] = relationship(back_populates="business")
    nfc_tags: Mapped[list["NfcTagModel"]] = relationship(back_populates="business")
    loyalty_programs: Mapped[list["LoyaltyProgramModel"]] = relationship(back_populates="business")


# ── Business Members ───────────────────────────────────

class BusinessMemberModel(Base):
    __tablename__ = "business_members"
    __table_args__ = (
        UniqueConstraint("business_id", "user_id", name="uq_business_user"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    business_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("businesses.id"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="staff")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utc_now)

    # Relationships
    business: Mapped["BusinessModel"] = relationship(back_populates="members")
    user: Mapped["UserModel"] = relationship(back_populates="memberships")


# ── NFC Tags ───────────────────────────────────────────

class NfcTagModel(Base):
    __tablename__ = "nfc_tags"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tag_uid: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    business_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("businesses.id"), nullable=False
    )
    label: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utc_now)

    # Relationships
    business: Mapped["BusinessModel"] = relationship(back_populates="nfc_tags")
    scans: Mapped[list["NfcScanModel"]] = relationship(back_populates="tag")


# ── NFC Scans ──────────────────────────────────────────

class NfcScanModel(Base):
    __tablename__ = "nfc_scans"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tag_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("nfc_tags.id"), nullable=False
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    business_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("businesses.id"), nullable=False, index=True
    )
    scanned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utc_now, index=True
    )
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    tag: Mapped["NfcTagModel"] = relationship(back_populates="scans")
    user: Mapped["UserModel"] = relationship(back_populates="scans")


# ── Loyalty Programs ───────────────────────────────────

class LoyaltyProgramModel(Base):
    __tablename__ = "loyalty_programs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    business_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("businesses.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    program_type: Mapped[str] = mapped_column(String(20), nullable=False, default="visits")
    visits_required: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    points_per_visit: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utc_now, onupdate=_utc_now
    )

    # Relationships
    business: Mapped["BusinessModel"] = relationship(back_populates="loyalty_programs")
    cards: Mapped[list["LoyaltyCardModel"]] = relationship(back_populates="program")
    rewards: Mapped[list["RewardModel"]] = relationship(back_populates="program")


# ── Loyalty Cards ──────────────────────────────────────

class LoyaltyCardModel(Base):
    __tablename__ = "loyalty_cards"
    __table_args__ = (
        UniqueConstraint("user_id", "program_id", name="uq_user_program"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    program_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("loyalty_programs.id"), nullable=False
    )
    business_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("businesses.id"), nullable=False
    )
    current_visits: Mapped[int] = mapped_column(Integer, default=0)
    current_points: Mapped[int] = mapped_column(Integer, default=0)
    total_visits: Mapped[int] = mapped_column(Integer, default=0)
    total_points: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(20), default="active")
    last_visit_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utc_now, onupdate=_utc_now
    )

    # Relationships
    user: Mapped["UserModel"] = relationship(back_populates="loyalty_cards")
    program: Mapped["LoyaltyProgramModel"] = relationship(back_populates="cards")


# ── Rewards ────────────────────────────────────────────

class RewardModel(Base):
    __tablename__ = "rewards"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    program_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("loyalty_programs.id"), nullable=False
    )
    business_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("businesses.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    reward_type: Mapped[str] = mapped_column(String(20), nullable=False, default="discount_pct")
    value: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    points_cost: Mapped[int] = mapped_column(Integer, default=0)
    visits_cost: Mapped[int] = mapped_column(Integer, default=0)
    stock: Mapped[int] = mapped_column(Integer, default=-1)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utc_now)

    # Relationships
    program: Mapped["LoyaltyProgramModel"] = relationship(back_populates="rewards")
    redemptions: Mapped[list["RedemptionModel"]] = relationship(back_populates="reward")


# ── Redemptions ────────────────────────────────────────

class RedemptionModel(Base):
    __tablename__ = "redemptions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    reward_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("rewards.id"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    business_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("businesses.id"), nullable=False
    )
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    redeemed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utc_now)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    reward: Mapped["RewardModel"] = relationship(back_populates="redemptions")
    user: Mapped["UserModel"] = relationship(back_populates="redemptions")


# ── Notification Campaigns ─────────────────────────────

class NotificationCampaignModel(Base):
    __tablename__ = "notification_campaigns"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    business_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("businesses.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    target_type: Mapped[str] = mapped_column(String(20), nullable=False, default="all")
    inactive_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    channel: Mapped[str] = mapped_column(String(20), default="email")
    status: Mapped[str] = mapped_column(String(20), default="draft")
    scheduled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utc_now)

    # Relationships
    logs: Mapped[list["NotificationLogModel"]] = relationship(back_populates="campaign")


# ── Notification Logs ──────────────────────────────────

class NotificationLogModel(Base):
    __tablename__ = "notification_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    campaign_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("notification_campaigns.id"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    channel: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="sent")
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utc_now)

    # Relationships
    campaign: Mapped["NotificationCampaignModel"] = relationship(back_populates="logs")
