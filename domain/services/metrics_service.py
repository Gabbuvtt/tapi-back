"""
Metrics service — aggregates data from multiple sources for the dashboard.
"""

from datetime import datetime, timedelta, timezone
from uuid import UUID

from domain.repositories.nfc_repository import NfcRepository
from domain.repositories.review_repository import ReviewRepository
from domain.repositories.loyalty_repository import LoyaltyRepository


class MetricsService:
    """Service for aggregating business dashboard metrics."""

    def __init__(
        self,
        nfc_repo: NfcRepository,
        review_repo: ReviewRepository,
        loyalty_repo: LoyaltyRepository,
    ):
        self._nfc_repo = nfc_repo
        self._review_repo = review_repo
        self._loyalty_repo = loyalty_repo

    async def get_dashboard_metrics(
        self, business_id: UUID, period_days: int = 30
    ) -> dict:
        """
        Get consolidated dashboard metrics for a business.

        Args:
            business_id: The business ID.
            period_days: Number of days to look back (default 30).

        Returns:
            dict with all dashboard KPIs.
        """
        now = datetime.now(timezone.utc)
        start_date = now - timedelta(days=period_days)

        # Parallel aggregation from multiple sources
        total_scans = await self._nfc_repo.count_scans(
            business_id, start_date=start_date, end_date=now
        )
        unique_visitors = await self._nfc_repo.count_unique_users(
            business_id, start_date=start_date, end_date=now
        )
        scan_timeline = await self._nfc_repo.get_scan_timeline(
            business_id, start_date=start_date, end_date=now
        )

        review_stats = await self._review_repo.get_stats(business_id)

        active_cards = await self._loyalty_repo.get_active_cards_count(business_id)
        total_redeemed = await self._loyalty_repo.get_total_redeemed(business_id)

        return {
            "period": f"{period_days}d",
            "total_scans": total_scans,
            "unique_visitors": unique_visitors,
            "returning_visitors": max(0, total_scans - unique_visitors),
            "total_reviews": review_stats.get("total", 0),
            "avg_rating": review_stats.get("avg_rating", 0.0),
            "reviews_sent_to_google": review_stats.get("sent_to_google_count", 0),
            "active_loyalty_cards": active_cards,
            "rewards_redeemed": total_redeemed,
            "scan_timeline": scan_timeline,
        }
