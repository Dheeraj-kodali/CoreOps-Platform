import csv
import io
import json
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User
from app.api.deps import require_permission
from app.core.rbac import PERM_ANALYTICS_READ
from app.services.analytics_service import AnalyticsService
from app.schemas.dashboard_v2 import (
    DashboardOverviewResponse, VisitorAnalyticsResponse,
    CommunicationMetricsResponse, SyncMetricsResponse, AuditMetricsResponse,
    AudienceAnalyticsResponse, SystemHealthResponse, DashboardExportRequest
)

router = APIRouter()


@router.get("/overview", response_model=DashboardOverviewResponse)
async def get_dashboard_overview(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(PERM_ANALYTICS_READ)),
):
    """GET v2 Owner Dashboard Overview (Read-Only)."""
    temple_id = getattr(request.state, "temple_id", "SKSA_MAIN")
    service = AnalyticsService(db)

    visitor_res = await service.get_visitor_metrics(temple_id)
    comm_res = await service.get_communication_metrics(temple_id)
    sync_res = await service.get_sync_metrics(temple_id)
    audit_res = await service.get_audit_metrics(temple_id)
    health_res = await service.get_system_health()

    return DashboardOverviewResponse(
        visitor_metrics=visitor_res.live,
        communication=comm_res,
        synchronization=sync_res,
        audit=audit_res,
        system_health_status=health_res.status,
        refresh_interval_seconds=30
    )


@router.get("/visitor-analytics", response_model=VisitorAnalyticsResponse)
async def get_visitor_analytics(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(PERM_ANALYTICS_READ)),
):
    """GET v2 Visitor Analytics Metrics."""
    temple_id = getattr(request.state, "temple_id", "SKSA_MAIN")
    service = AnalyticsService(db)
    return await service.get_visitor_metrics(temple_id)


@router.get("/communication-metrics", response_model=CommunicationMetricsResponse)
async def get_communication_metrics(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(PERM_ANALYTICS_READ)),
):
    """GET v2 Communication Metrics."""
    temple_id = getattr(request.state, "temple_id", "SKSA_MAIN")
    service = AnalyticsService(db)
    return await service.get_communication_metrics(temple_id)


@router.get("/sync-metrics", response_model=SyncMetricsResponse)
async def get_sync_metrics(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(PERM_ANALYTICS_READ)),
):
    """GET v2 Synchronization Protocol Metrics."""
    temple_id = getattr(request.state, "temple_id", "SKSA_MAIN")
    service = AnalyticsService(db)
    return await service.get_sync_metrics(temple_id)


@router.get("/audit-metrics", response_model=AuditMetricsResponse)
async def get_audit_metrics(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(PERM_ANALYTICS_READ)),
):
    """GET v2 Audit System Metrics."""
    temple_id = getattr(request.state, "temple_id", "SKSA_MAIN")
    service = AnalyticsService(db)
    return await service.get_audit_metrics(temple_id)


@router.get("/audience-analytics", response_model=AudienceAnalyticsResponse)
async def get_audience_analytics(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(PERM_ANALYTICS_READ)),
):
    """GET v2 Audience & Devotee Analytics."""
    temple_id = getattr(request.state, "temple_id", "SKSA_MAIN")
    service = AnalyticsService(db)
    return await service.get_audience_analytics(temple_id)


@router.get("/system-health", response_model=SystemHealthResponse)
async def get_system_health(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(PERM_ANALYTICS_READ)),
):
    """GET v2 System Health & Infrastructure Diagnostics."""
    service = AnalyticsService(db)
    return await service.get_system_health()


@router.post("/export")
async def export_dashboard_analytics(
    export_req: DashboardExportRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(PERM_ANALYTICS_READ)),
):
    """POST v2 Dashboard Analytics Export (PDF, Excel, CSV, JSON)."""
    temple_id = export_req.temple_id or getattr(request.state, "temple_id", "SKSA_MAIN")
    service = AnalyticsService(db)

    visitor = await service.get_visitor_metrics(temple_id)
    comm = await service.get_communication_metrics(temple_id)
    sync = await service.get_sync_metrics(temple_id)
    audit = await service.get_audit_metrics(temple_id)
    audience = await service.get_audience_analytics(temple_id)

    export_data = {
        "temple_id": temple_id,
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "visitor_metrics": visitor.model_dump(),
        "communication_metrics": comm.model_dump(),
        "sync_metrics": sync.model_dump(),
        "audit_metrics": audit.model_dump(),
        "audience_analytics": audience.model_dump(),
    }

    fmt = export_req.format.lower()
    ts = int(datetime.now(timezone.utc).timestamp())

    if fmt == "pdf":
        # Formatted PDF plain document stream
        pdf_content = f"--- TEMPLE OWNER ANALYTICS REPORT ---\nTemple ID: {temple_id}\nDate: {export_data['exported_at']}\n\n"
        pdf_content += f"VISITOR METRICS:\nLive: {visitor.live.live_visitors}\nToday: {visitor.live.today_visitors}\nWeekly: {visitor.live.weekly_visitors}\nMonthly: {visitor.live.monthly_visitors}\n\n"
        pdf_content += f"COMMUNICATION METRICS:\nSent: {comm.messages_sent}\nDelivered: {comm.delivered}\nDelivery Rate: {comm.delivery_rate}%\n\n"
        pdf_content += f"SYNC METRICS:\nSuccessful Syncs: {sync.successful_syncs}\nFailed Syncs: {sync.failed_syncs}\nSuccess Rate: {sync.success_rate}%\n"

        return Response(
            content=pdf_content.encode('utf-8'),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=dashboard_report_{ts}.pdf"}
        )

    elif fmt in ("excel", "csv"):
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Category", "Metric", "Value"])
        writer.writerow(["Visitor", "Live Visitors", visitor.live.live_visitors])
        writer.writerow(["Visitor", "Today Visitors", visitor.live.today_visitors])
        writer.writerow(["Visitor", "Weekly Visitors", visitor.live.weekly_visitors])
        writer.writerow(["Visitor", "Monthly Visitors", visitor.live.monthly_visitors])
        writer.writerow(["Communication", "Sent", comm.messages_sent])
        writer.writerow(["Communication", "Delivered", comm.delivered])
        writer.writerow(["Communication", "Delivery Rate (%)", comm.delivery_rate])
        writer.writerow(["Sync", "Successful Syncs", sync.successful_syncs])
        writer.writerow(["Sync", "Success Rate (%)", sync.success_rate])
        writer.writerow(["Audience", "Total Devotees", audience.total_devotees])

        output.seek(0)
        media = "application/vnd.ms-excel" if fmt == "excel" else "text/csv"
        ext = "xlsx" if fmt == "excel" else "csv"

        return StreamingResponse(
            io.BytesIO(output.getvalue().encode('utf-8')),
            media_type=media,
            headers={"Content-Disposition": f"attachment; filename=dashboard_report_{ts}.{ext}"}
        )

    else:
        # JSON format default
        return Response(
            content=json.dumps(export_data, indent=2),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename=dashboard_report_{ts}.json"}
        )
