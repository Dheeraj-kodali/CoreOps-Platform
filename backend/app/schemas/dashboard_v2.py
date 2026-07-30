from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class LiveVisitorMetrics(BaseModel):
    live_visitors: int
    today_visitors: int
    weekly_visitors: int
    monthly_visitors: int
    yearly_visitors: int
    repeat_visitors: int
    first_time_visitors: int


class DistributionItem(BaseModel):
    label: str
    count: int
    percentage: float


class HourlyTrendItem(BaseModel):
    hour: int  # 0 to 23
    count: int


class DailyTrendItem(BaseModel):
    date: str
    count: int


class VisitorAnalyticsResponse(BaseModel):
    live: LiveVisitorMetrics
    hourly_trends: List[HourlyTrendItem]
    daily_trends: List[DailyTrendItem]
    village_distribution: List[DistributionItem]
    purpose_distribution: List[DistributionItem]
    peak_visiting_hours: List[HourlyTrendItem]


class CommunicationMetricsResponse(BaseModel):
    messages_sent: int
    delivered: int
    failed: int
    pending: int
    delivery_rate: float


class SyncMetricsResponse(BaseModel):
    pending_queue: int
    successful_syncs: int
    failed_syncs: int
    last_sync_timestamp: Optional[str] = None
    average_duration_ms: float
    success_rate: float


class AuditMetricsResponse(BaseModel):
    critical_events: int
    warnings: int
    errors: int
    failed_logins: int
    backups: int
    restores: int


class AudienceAnalyticsResponse(BaseModel):
    total_devotees: int
    visited_last_7_days: int
    visited_last_30_days: int
    visited_last_90_days: int
    repeat_visitors: int
    first_time_visitors: int
    village_breakdown: List[DistributionItem]
    purpose_breakdown: List[DistributionItem]
    visit_frequency_average: float


class SystemHealthComponent(BaseModel):
    status: str  # HEALTHY, DEGRADED, DOWN
    latency_ms: float
    details: Optional[Dict[str, Any]] = None


class SystemHealthResponse(BaseModel):
    status: str  # HEALTHY, DEGRADED, DOWN
    backend: SystemHealthComponent
    database: SystemHealthComponent
    synchronization: SystemHealthComponent
    whatsapp: SystemHealthComponent
    storage: SystemHealthComponent
    version: str = "2.0.0"


class DashboardOverviewResponse(BaseModel):
    visitor_metrics: LiveVisitorMetrics
    communication: CommunicationMetricsResponse
    synchronization: SyncMetricsResponse
    audit: AuditMetricsResponse
    system_health_status: str
    refresh_interval_seconds: int = 30


class DashboardExportRequest(BaseModel):
    temple_id: Optional[str] = "SKSA_MAIN"
    metric_type: str = Field("all", description="Metrics to export: visitor, communication, sync, audit, audience, all")
    format: str = Field("json", description="Export format: pdf, excel, csv, json")
