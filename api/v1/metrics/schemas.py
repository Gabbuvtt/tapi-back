"""
Pydantic schemas for the Metrics module.
"""

from pydantic import BaseModel, Field


class TimelinePoint(BaseModel):
    """A single data point in a timeline."""
    date: str
    count: int


class DashboardMetricsResponse(BaseModel):
    """Consolidated dashboard metrics."""
    period: str
    total_scans: int
    unique_visitors: int
    returning_visitors: int
    total_reviews: int
    avg_rating: float
    reviews_sent_to_google: int
    active_loyalty_cards: int
    rewards_redeemed: int
    scan_timeline: list[TimelinePoint]
