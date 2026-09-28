"""
NFC repository — PostgreSQL implementation.
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import select, func, cast, Date
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.nfc_scan import NfcScan, NfcTag
from domain.repositories.nfc_repository import NfcRepository
from infraestructure.database.postgres.models import NfcScanModel, NfcTagModel


class PostgresNfcRepository(NfcRepository):
    """Concrete NFC repository backed by PostgreSQL."""

    def __init__(self, session: AsyncSession):
        self._session = session

    # ── Tag Mappers ─────────────────────────────────────

    @staticmethod
    def _tag_to_entity(model: NfcTagModel) -> NfcTag:
        return NfcTag(
            id=model.id, tag_uid=model.tag_uid, business_id=model.business_id,
            label=model.label, is_active=model.is_active, created_at=model.created_at,
        )

    @staticmethod
    def _scan_to_entity(model: NfcScanModel) -> NfcScan:
        return NfcScan(
            id=model.id, tag_id=model.tag_id, user_id=model.user_id,
            business_id=model.business_id, scanned_at=model.scanned_at,
            ip_address=model.ip_address, user_agent=model.user_agent,
        )

    # ── Tags ────────────────────────────────────────────

    async def create_tag(self, tag: NfcTag) -> NfcTag:
        model = NfcTagModel(
            id=tag.id, tag_uid=tag.tag_uid, business_id=tag.business_id,
            label=tag.label, is_active=tag.is_active,
        )
        self._session.add(model)
        await self._session.flush()
        return self._tag_to_entity(model)

    async def get_tag_by_uid(self, tag_uid: str) -> NfcTag | None:
        result = await self._session.execute(
            select(NfcTagModel).where(NfcTagModel.tag_uid == tag_uid)
        )
        model = result.scalar_one_or_none()
        return self._tag_to_entity(model) if model else None

    async def get_tags_by_business(self, business_id: UUID) -> list[NfcTag]:
        result = await self._session.execute(
            select(NfcTagModel).where(NfcTagModel.business_id == business_id)
        )
        return [self._tag_to_entity(m) for m in result.scalars().all()]

    async def deactivate_tag(self, tag_id: UUID) -> None:
        result = await self._session.execute(
            select(NfcTagModel).where(NfcTagModel.id == tag_id)
        )
        model = result.scalar_one_or_none()
        if model:
            model.is_active = False
            await self._session.flush()

    # ── Scans ───────────────────────────────────────────

    async def create_scan(self, scan: NfcScan) -> NfcScan:
        model = NfcScanModel(
            id=scan.id, tag_id=scan.tag_id, user_id=scan.user_id,
            business_id=scan.business_id, scanned_at=scan.scanned_at,
            ip_address=scan.ip_address, user_agent=scan.user_agent,
        )
        self._session.add(model)
        await self._session.flush()
        return self._scan_to_entity(model)

    async def get_scans_by_business(
        self, business_id: UUID, start_date: datetime | None = None,
        end_date: datetime | None = None, limit: int = 100, offset: int = 0,
    ) -> list[NfcScan]:
        query = select(NfcScanModel).where(NfcScanModel.business_id == business_id)
        if start_date:
            query = query.where(NfcScanModel.scanned_at >= start_date)
        if end_date:
            query = query.where(NfcScanModel.scanned_at <= end_date)
        query = query.order_by(NfcScanModel.scanned_at.desc()).limit(limit).offset(offset)
        result = await self._session.execute(query)
        return [self._scan_to_entity(m) for m in result.scalars().all()]

    async def count_scans(
        self, business_id: UUID, start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> int:
        query = select(func.count(NfcScanModel.id)).where(
            NfcScanModel.business_id == business_id
        )
        if start_date:
            query = query.where(NfcScanModel.scanned_at >= start_date)
        if end_date:
            query = query.where(NfcScanModel.scanned_at <= end_date)
        result = await self._session.execute(query)
        return result.scalar() or 0

    async def count_unique_users(
        self, business_id: UUID, start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> int:
        query = select(func.count(func.distinct(NfcScanModel.user_id))).where(
            NfcScanModel.business_id == business_id,
            NfcScanModel.user_id.isnot(None),
        )
        if start_date:
            query = query.where(NfcScanModel.scanned_at >= start_date)
        if end_date:
            query = query.where(NfcScanModel.scanned_at <= end_date)
        result = await self._session.execute(query)
        return result.scalar() or 0

    async def get_user_scan_count(self, user_id: UUID, business_id: UUID) -> int:
        result = await self._session.execute(
            select(func.count(NfcScanModel.id)).where(
                NfcScanModel.user_id == user_id,
                NfcScanModel.business_id == business_id,
            )
        )
        return result.scalar() or 0

    async def get_scan_timeline(
        self, business_id: UUID, start_date: datetime, end_date: datetime
    ) -> list[dict]:
        result = await self._session.execute(
            select(
                cast(NfcScanModel.scanned_at, Date).label("date"),
                func.count(NfcScanModel.id).label("count"),
            )
            .where(
                NfcScanModel.business_id == business_id,
                NfcScanModel.scanned_at >= start_date,
                NfcScanModel.scanned_at <= end_date,
            )
            .group_by(cast(NfcScanModel.scanned_at, Date))
            .order_by(cast(NfcScanModel.scanned_at, Date))
        )
        return [
            {"date": str(row.date), "count": row.count}
            for row in result.all()
        ]
