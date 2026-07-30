from typing import List
from pydantic import BaseModel


class LiveStatistics(BaseModel):
    active_volunteers: int
    visitors_last_hour: int
    pending_sync_queue: int


class DashboardSummaryResponse(BaseModel):
    today_visitors: int
    weekly_visitors: int
    monthly_visitors: int
    yearly_visitors: int
    total_visitors: int
    live_statistics: LiveStatistics


class PurposeAnalyticsItem(BaseModel):
    purpose_id: int
    name_en: str
    name_te: str
    count: int
    percentage: float


class PurposeAnalyticsResponse(BaseModel):
    total: int
    breakdown: List[PurposeAnalyticsItem]


class HourlyTrendItem(BaseModel):
    hour: str
    count: int


class DailyTrendItem(BaseModel):
    date: str
    count: int
