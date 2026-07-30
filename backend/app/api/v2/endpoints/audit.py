import csv
import io
import json
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User
from app.api.deps import require_permission
from app.core.rbac import PERM_AUDIT_READ
from app.schemas.audit_v2 import (
    AuditSearchRequest, AuditSearchResponse, AuditRecordItem,
    AuditExportRequest
)
from app.repositories.audit_repository import AuditRepository

router = APIRouter()


@router.post("/search", response_model=AuditSearchResponse)
async def search_audit_records(
    search_req: AuditSearchRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(PERM_AUDIT_READ)),
):
    """v2 Immutable Audit Search API.
    
    Returns filtered and paginated immutable audit event records.
    """
    repo = AuditRepository(db)

    # Parse date filters
    dt_from: Optional[datetime] = None
    dt_to: Optional[datetime] = None
    if search_req.date_from:
        try:
            dt_from = datetime.fromisoformat(search_req.date_from.replace("Z", "+00:00"))
        except ValueError:
            dt_from = None
    if search_req.date_to:
        try:
            dt_to = datetime.fromisoformat(search_req.date_to.replace("Z", "+00:00"))
        except ValueError:
            dt_to = None

    temple_id = search_req.temple_id or getattr(request.state, "temple_id", "SKSA_MAIN")

    records, total_count = await repo.search(
        temple_id=temple_id,
        action=search_req.action,
        severity=search_req.severity,
        entity_type=search_req.entity_type,
        user_id=search_req.user_id,
        date_from=dt_from,
        date_to=dt_to,
        page=search_req.page,
        page_size=search_req.page_size,
    )

    items = [
        AuditRecordItem(
            audit_id=r.audit_id,
            trace_id=r.trace_id,
            temple_id=r.temple_id,
            user_id=r.user_id,
            role=r.role,
            device_id=r.device_id,
            session_id=r.session_id,
            action=r.action,
            entity_type=r.entity_type,
            entity_id=r.entity_id,
            old_value=r.old_value,
            new_value=r.new_value,
            status=r.status,
            severity=r.severity,
            timestamp=r.timestamp.isoformat() if r.timestamp else datetime.now(timezone.utc).isoformat(),
            ip_address=r.ip_address,
            application_version=r.application_version,
            platform=r.platform,
            api_version=r.api_version,
            duration_ms=r.duration_ms,
        )
        for r in records
    ]

    total_pages = (total_count + search_req.page_size - 1) // search_req.page_size if search_req.page_size > 0 else 1

    return AuditSearchResponse(
        items=items,
        total_count=total_count,
        page=search_req.page,
        page_size=search_req.page_size,
        total_pages=total_pages,
    )


@router.post("/export")
async def export_audit_records(
    export_req: AuditExportRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(PERM_AUDIT_READ)),
):
    """v2 Immutable Audit Export API.
    
    Exports full audit trail records in CSV or JSON format.
    """
    repo = AuditRepository(db)

    dt_from: Optional[datetime] = None
    dt_to: Optional[datetime] = None
    if export_req.date_from:
        try:
            dt_from = datetime.fromisoformat(export_req.date_from.replace("Z", "+00:00"))
        except ValueError:
            dt_from = None
    if export_req.date_to:
        try:
            dt_to = datetime.fromisoformat(export_req.date_to.replace("Z", "+00:00"))
        except ValueError:
            dt_to = None

    temple_id = export_req.temple_id or getattr(request.state, "temple_id", "SKSA_MAIN")

    records, _ = await repo.search(
        temple_id=temple_id,
        action=export_req.action,
        severity=export_req.severity,
        entity_type=export_req.entity_type,
        user_id=export_req.user_id,
        date_from=dt_from,
        date_to=dt_to,
        page=1,
        page_size=10000,
    )

    if export_req.format.lower() == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "audit_id", "trace_id", "temple_id", "user_id", "role", "device_id",
            "session_id", "action", "entity_type", "entity_id", "status", "severity",
            "timestamp", "ip_address", "application_version", "platform", "api_version", "duration_ms"
        ])
        for r in records:
            writer.writerow([
                r.audit_id, r.trace_id, r.temple_id, r.user_id, r.role, r.device_id,
                r.session_id, r.action, r.entity_type, r.entity_id, r.status, r.severity,
                r.timestamp.isoformat() if r.timestamp else "", r.ip_address,
                r.application_version, r.platform, r.api_version, r.duration_ms
            ])
        
        output.seek(0)
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode('utf-8')),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=audit_export_{int(datetime.now(timezone.utc).timestamp())}.csv"}
        )

    else:
        # JSON format
        export_data = [
            {
                "audit_id": r.audit_id,
                "trace_id": r.trace_id,
                "temple_id": r.temple_id,
                "user_id": r.user_id,
                "role": r.role,
                "device_id": r.device_id,
                "session_id": r.session_id,
                "action": r.action,
                "entity_type": r.entity_type,
                "entity_id": r.entity_id,
                "old_value": r.old_value,
                "new_value": r.new_value,
                "status": r.status,
                "severity": r.severity,
                "timestamp": r.timestamp.isoformat() if r.timestamp else "",
                "ip_address": r.ip_address,
                "application_version": r.application_version,
                "platform": r.platform,
                "api_version": r.api_version,
                "duration_ms": r.duration_ms,
            }
            for r in records
        ]
        return Response(
            content=json.dumps(export_data, indent=2),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename=audit_export_{int(datetime.now(timezone.utc).timestamp())}.json"}
        )
