import json
import uuid
from datetime import datetime, timezone
from typing import List, Tuple, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

from app.models.audit import AuditRecord
from app.core.exceptions import ImmutableAuditException


class AuditRepository:
    """Enterprise Append-Only Audit Repository.
    
    Enforces strict immutability rules (NO updates, NO deletions).
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        action: str,
        entity_type: str,
        trace_id: Optional[str] = None,
        temple_id: Optional[str] = "SKSA_MAIN",
        user_id: Optional[str] = None,
        role: Optional[str] = None,
        device_id: Optional[str] = None,
        session_id: Optional[str] = None,
        entity_id: Optional[str] = None,
        old_value: Optional[Dict[str, Any]] = None,
        new_value: Optional[Dict[str, Any]] = None,
        status: str = "SUCCESS",
        severity: str = "INFO",
        ip_address: Optional[str] = None,
        application_version: str = "2.0.0",
        platform: str = "Backend-FastAPI",
        api_version: str = "v2.0",
        duration_ms: float = 0.0,
    ) -> AuditRecord:
        """Appends a new immutable AuditRecord."""
        record = AuditRecord(
            audit_id=str(uuid.uuid4()),
            trace_id=trace_id or str(uuid.uuid4()),
            temple_id=temple_id or "SKSA_MAIN",
            user_id=user_id,
            role=role,
            device_id=device_id,
            session_id=session_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            old_value=json.dumps(old_value) if old_value else None,
            new_value=json.dumps(new_value) if new_value else None,
            status=status,
            severity=severity,
            timestamp=datetime.now(timezone.utc),
            ip_address=ip_address,
            application_version=application_version,
            platform=platform,
            api_version=api_version,
            duration_ms=duration_ms,
        )
        self.db.add(record)
        await self.db.commit()
        await self.db.refresh(record)
        return record

    async def update(self, *args, **kwargs):
        """Strictly prohibited update operation."""
        raise ImmutableAuditException("Audit records are immutable and append-only. UPDATE operations are strictly prohibited.")

    async def delete(self, *args, **kwargs):
        """Strictly prohibited delete operation."""
        raise ImmutableAuditException("Audit records are immutable and append-only. DELETE operations are strictly prohibited.")

    async def search(
        self,
        temple_id: Optional[str] = None,
        action: Optional[str] = None,
        severity: Optional[str] = None,
        entity_type: Optional[str] = None,
        user_id: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> Tuple[List[AuditRecord], int]:
        """Queries audit records with filters & pagination."""
        query = select(AuditRecord)

        if temple_id:
            query = query.filter(AuditRecord.temple_id == temple_id)
        if action:
            query = query.filter(AuditRecord.action == action)
        if severity:
            query = query.filter(AuditRecord.severity == severity)
        if entity_type:
            query = query.filter(AuditRecord.entity_type == entity_type)
        if user_id:
            query = query.filter(AuditRecord.user_id == user_id)
        if date_from:
            query = query.filter(AuditRecord.timestamp >= date_from)
        if date_to:
            query = query.filter(AuditRecord.timestamp <= date_to)

        # Count total matching records
        count_query = select(func.count()).select_from(query.subquery())
        count_res = await self.db.execute(count_query)
        total_count = count_res.scalar() or 0

        # Execute paginated query
        offset = (page - 1) * page_size
        query = query.order_by(AuditRecord.timestamp.desc()).offset(offset).limit(page_size)
        res = await self.db.execute(query)
        records = res.scalars().all()

        return records, total_count
