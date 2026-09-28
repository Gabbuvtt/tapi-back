"""
Metrics API endpoints.

GET /metrics/dashboard — Consolidated dashboard metrics
"""

from uuid import UUID

from fastapi import APIRouter, Depends, Query

from api.dependencies import get_current_user_id, get_metrics_service
from api.v1.metrics.schemas import DashboardMetricsResponse, TimelinePoint
from domain.services.metrics_service import MetricsService

router = APIRouter()


@router.get(
    "/dashboard",
    response_model=DashboardMetricsResponse,
    summary="Dashboard metrics",
    description=(
        "Get consolidated metrics for the business dashboard. "
        "Aggregates scans, reviews, loyalty, and timeline data."
    ),
)
async def get_dashboard_metrics(
    business_id: UUID = Query(..., description="Business ID"),
    period: int = Query(30, ge=1, le=365, description="Period in days"),
    user_id: UUID = Depends(get_current_user_id),
    metrics_service: MetricsService = Depends(get_metrics_service),
):
    metrics = await metrics_service.get_dashboard_metrics(
        business_id=business_id,
        period_days=period,
    )
    return DashboardMetricsResponse(
        period=metrics["period"],
        total_scans=metrics["total_scans"],
        unique_visitors=metrics["unique_visitors"],
        returning_visitors=metrics["returning_visitors"],
        total_reviews=metrics["total_reviews"],
        avg_rating=metrics["avg_rating"],
        reviews_sent_to_google=metrics["reviews_sent_to_google"],
        active_loyalty_cards=metrics["active_loyalty_cards"],
        rewards_redeemed=metrics["rewards_redeemed"],
        scan_timeline=[
            TimelinePoint(date=p["date"], count=p["count"])
            for p in metrics.get("scan_timeline", [])
        ],
    )
