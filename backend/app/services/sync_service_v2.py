import json
import time
import hashlib
import uuid
from datetime import datetime, timezone, date as date_cls
from typing import List, Tuple, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_
from sqlalchemy.orm import selectinload

from app.models.sync import SyncQueue, SyncToken
from app.models.visit_session import VisitSession
from app.models.visitor_profile import VisitorProfile
from app.models.visitor import Visitor
from app.models.person import Person
from app.models.user import User
from app.schemas.sync_v2 import (
    BatchUploadRequest, BatchUploadResponse, SyncItemResponse,
    SyncMetrics, SyncEventItem, DeltaDownloadRequest, DeltaDownloadResponse,
    DeltaEntityChange
)
from app.core.audit_hook import record_audit_event


class DeltaSyncServiceV2:
    """Enterprise Domain Service for Delta Synchronization Protocol v2.0."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def process_batch_upload(
        self,
        request: BatchUploadRequest,
        current_user: User,
        payload_bytes_len: int = 0
    ) -> BatchUploadResponse:
        start_time = time.perf_counter()
        results: List[SyncItemResponse] = []
        
        success_count = 0
        duplicates_count = 0
        conflicts_count = 0
        failed_count = 0
        temple_id = request.temple_id or "SKSA_MAIN"

        await record_audit_event(
            self.db,
            action="SYNC_START",
            entity_type="SYNC",
            user_id=current_user.id,
            temple_id=temple_id,
            device_id=request.client_id,
            severity="INFO",
            new_value={"events_count": len(request.events), "client_id": request.client_id}
        )

        if request.batch_sha256:
            raw_payload_str = json.dumps([e.dict() for e in request.events], sort_keys=True)
            calculated_hash = hashlib.sha256(raw_payload_str.encode('utf-8')).hexdigest()
            if calculated_hash.lower() != request.batch_sha256.lower():
                for event in request.events:
                    results.append(
                        SyncItemResponse(
                            event_id=event.event_id,
                            entity_id=event.entity_id,
                            status="FAILED",
                            retryable=True,
                            error_message="Batch SHA-256 integrity checksum mismatch",
                            server_synced_at=datetime.now(timezone.utc).isoformat(),
                        )
                    )
                latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
                return BatchUploadResponse(
                    client_id=request.client_id,
                    next_sync_token=request.last_sync_token or "sync_token_0",
                    results=results,
                    metrics=SyncMetrics(
                        latency_ms=latency_ms,
                        items_processed=len(request.events),
                        success_count=0,
                        duplicates_count=0,
                        conflicts_count=0,
                        failed_count=len(request.events),
                        payload_size_bytes=payload_bytes_len
                    )
                )

        for event in request.events:
            item_result, status_type = await self._process_single_event(
                event=event,
                client_id=request.client_id,
                temple_id=temple_id,
                user_id=current_user.id
            )
            results.append(item_result)

            if status_type == "SYNCED":
                success_count += 1
            elif status_type == "DUPLICATE":
                duplicates_count += 1
            elif status_type == "CONFLICT":
                conflicts_count += 1
            elif status_type == "FAILED":
                failed_count += 1

        now_utc = datetime.now(timezone.utc)
        next_sync_token = f"token_{int(now_utc.timestamp())}_{request.client_id[:8]}"

        token_res = await self.db.execute(
            select(SyncToken).filter(
                SyncToken.client_id == request.client_id,
                SyncToken.temple_id == temple_id
            )
        )
        sync_token_record = token_res.scalars().first()
        if sync_token_record:
            sync_token_record.last_synced_token = next_sync_token
            sync_token_record.last_synced_at = now_utc
        else:
            sync_token_record = SyncToken(
                temple_id=temple_id,
                client_id=request.client_id,
                device_name="Mobile Edge Device",
                last_synced_token=next_sync_token,
                last_synced_at=now_utc
            )
            self.db.add(sync_token_record)

        await self.db.commit()

        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
        metrics = SyncMetrics(
            latency_ms=latency_ms,
            items_processed=len(request.events),
            success_count=success_count,
            duplicates_count=duplicates_count,
            conflicts_count=conflicts_count,
            failed_count=failed_count,
            payload_size_bytes=payload_bytes_len
        )

        return BatchUploadResponse(
            client_id=request.client_id,
            next_sync_token=next_sync_token,
            results=results,
            metrics=metrics
        )

    async def _process_single_event(
        self,
        event: SyncEventItem,
        client_id: str,
        temple_id: str,
        user_id: str
    ) -> Tuple[SyncItemResponse, str]:
        now_iso = datetime.now(timezone.utc).isoformat()
        server_now = datetime.now(timezone.utc)

        if event.sha256_hash:
            payload_json_str = json.dumps(event.payload, sort_keys=True)
            calc_hash = hashlib.sha256(payload_json_str.encode('utf-8')).hexdigest()
            if calc_hash.lower() != event.sha256_hash.lower():
                return SyncItemResponse(
                    event_id=event.event_id,
                    entity_id=event.entity_id,
                    status="FAILED",
                    retryable=True,
                    error_message="Event payload SHA-256 hash mismatch",
                    server_synced_at=now_iso
                ), "FAILED"

        q_res = await self.db.execute(
            select(SyncQueue).filter(
                SyncQueue.visitor_uuid == event.event_id,
                SyncQueue.client_id == client_id
            )
        )
        existing_queue = q_res.scalars().first()
        if existing_queue and existing_queue.status in ("SYNCED", "DUPLICATE"):
            return SyncItemResponse(
                event_id=event.event_id,
                entity_id=event.entity_id,
                status="DUPLICATE",
                retryable=False,
                error_message=None,
                server_synced_at=existing_queue.server_synced_at.isoformat() if existing_queue.server_synced_at else now_iso
            ), "DUPLICATE"

        queue_record = SyncQueue(
            temple_id=temple_id,
            visitor_uuid=event.event_id,
            client_id=client_id,
            action_type=event.action,
            payload_json=json.dumps(event.payload),
            status="PENDING",
            client_timestamp=datetime.fromisoformat(event.client_timestamp.replace("Z", "+00:00")),
            server_synced_at=server_now
        )
        self.db.add(queue_record)

        try:
            if event.action == "CREATE":
                if event.entity_type in ("VISITOR", "VISIT_SESSION"):
                    # Check duplicate session by entity_id
                    s_res = await self.db.execute(select(VisitSession).filter(VisitSession.id == event.entity_id))
                    if s_res.scalars().first():
                        queue_record.status = "DUPLICATE"
                        return SyncItemResponse(
                            event_id=event.event_id,
                            entity_id=event.entity_id,
                            status="DUPLICATE",
                            retryable=False,
                            server_synced_at=now_iso
                        ), "DUPLICATE"

                    p = event.payload
                    phone = p.get("phone_number", p.get("phone", "+910000000000")).strip()
                    
                    # 1. Lookup/Create Profile
                    p_res = await self.db.execute(select(VisitorProfile).filter(VisitorProfile.phone_number == phone))
                    prof = p_res.scalars().first()

                    if not prof:
                        prof = VisitorProfile(
                            id=str(uuid.uuid4()),
                            visitor_id=p.get("visitor_id") or f"VIP-{str(uuid.uuid4())[:8].upper()}",
                            name=p.get("name", "Unknown Devotee"),
                            phone_number=phone,
                            village_name_custom=p.get("village", p.get("village_name_custom")),
                            gender=p.get("gender", "MALE"),
                            age=int(p.get("age", 30)),
                            default_purpose_id=p.get("purpose_id", p.get("purposeId")),
                            created_by=user_id,
                        )
                        self.db.add(prof)
                        await self.db.flush()

                    # 2. Create Visit Session
                    v_date_str = p.get("visitor_date", p.get("visit_date", p.get("date")))
                    v_date = datetime.strptime(v_date_str[:10], "%Y-%m-%d").date() if v_date_str else date_cls.today()
                    
                    v_time_str = p.get("visitor_time", p.get("check_in_time", p.get("time_in", "10:00:00")))
                    try:
                        v_time = datetime.strptime(v_time_str[:8], "%H:%M:%S").time()
                    except ValueError:
                        v_time = datetime.now().time()

                    new_session = VisitSession(
                        id=event.entity_id,
                        visitor_profile_id=prof.id,
                        temple_id=temple_id,
                        visit_date=v_date,
                        check_in_time=v_time,
                        persons_count=int(p.get("persons_count", p.get("personsCount", 1))),
                        purpose_id=p.get("purpose_id", p.get("purposeId", "3ef2daff-d716-4285-ac7c-81e702530b44")),
                        notes=p.get("notes"),
                        volunteer_id=user_id,
                        status=p.get("status", "INSIDE"),
                        sync_status="SYNCED",
                    )
                    self.db.add(new_session)
                    queue_record.status = "SYNCED"

                    # Also populate legacy table for backwards compatibility
                    v_legacy = Visitor(
                        id=event.entity_id,
                        visitor_uuid=event.entity_id,
                        temple_id=temple_id,
                        name=prof.name,
                        phone_number=prof.phone_number,
                        gender=prof.gender,
                        age=prof.age,
                        persons_count=new_session.persons_count,
                        village_name_custom=prof.village_name_custom,
                        purpose_id=new_session.purpose_id,
                        visitor_date=new_session.visit_date,
                        visitor_time=new_session.check_in_time,
                        volunteer_id=user_id,
                        notes=new_session.notes,
                        sync_status="SYNCED"
                    )
                    self.db.add(v_legacy)

                    return SyncItemResponse(
                        event_id=event.event_id,
                        entity_id=event.entity_id,
                        status="SYNCED",
                        retryable=False,
                        server_synced_at=now_iso
                    ), "SYNCED"

            elif event.action in ("UPDATE", "CHECKOUT"):
                s_res = await self.db.execute(select(VisitSession).filter(VisitSession.id == event.entity_id))
                existing_session = s_res.scalars().first()
                if not existing_session:
                    queue_record.status = "CONFLICT"
                    return SyncItemResponse(
                        event_id=event.event_id,
                        entity_id=event.entity_id,
                        status="CONFLICT",
                        retryable=False,
                        error_message="Target visit session record not found on server for update",
                        server_synced_at=now_iso
                    ), "CONFLICT"

                p = event.payload
                if event.action == "CHECKOUT":
                    time_out_str = p.get("time_out", p.get("timeOut", "18:00:00"))
                    try:
                        existing_session.check_out_time = datetime.strptime(time_out_str[:8], "%H:%M:%S").time()
                    except ValueError:
                        existing_session.check_out_time = datetime.now().time()
                    existing_session.status = "CHECKED_OUT"
                else:
                    if "notes" in p:
                        existing_session.notes = p["notes"]

                existing_session.sync_status = "SYNCED"
                queue_record.status = "SYNCED"
                return SyncItemResponse(
                    event_id=event.event_id,
                    entity_id=event.entity_id,
                    status="SYNCED",
                    retryable=False,
                    server_synced_at=now_iso
                ), "SYNCED"

            queue_record.status = "SYNCED"
            return SyncItemResponse(
                event_id=event.event_id,
                entity_id=event.entity_id,
                status="SYNCED",
                retryable=False,
                server_synced_at=now_iso
            ), "SYNCED"

        except Exception as err:
            queue_record.status = "FAILED"
            queue_record.error_message = str(err)
            return SyncItemResponse(
                event_id=event.event_id,
                entity_id=event.entity_id,
                status="FAILED",
                retryable=True,
                error_message=str(err),
                server_synced_at=now_iso
            ), "FAILED"

    async def process_delta_download(
        self,
        request: DeltaDownloadRequest,
        temple_id: str = "SKSA_MAIN"
    ) -> DeltaDownloadResponse:
        server_now = datetime.now(timezone.utc)
        now_iso = server_now.isoformat()

        threshold_dt: Optional[datetime] = None
        if request.since_timestamp:
            try:
                threshold_dt = datetime.fromisoformat(request.since_timestamp.replace("Z", "+00:00"))
            except ValueError:
                threshold_dt = None

        query = (
            select(VisitSession)
            .options(selectinload(VisitSession.visitor_profile), selectinload(VisitSession.purpose))
            .filter(
                or_(VisitSession.temple_id == temple_id, VisitSession.temple_id.is_(None)),
                VisitSession.is_deleted.is_(False)
            )
        )
        if threshold_dt:
            query = query.filter(VisitSession.updated_at >= threshold_dt)

        query = query.order_by(VisitSession.updated_at.asc()).limit(request.limit + 1)
        res = await self.db.execute(query)
        sessions = res.scalars().all()

        has_more = len(sessions) > request.limit
        if has_more:
            sessions = sessions[:request.limit]

        changes: List[DeltaEntityChange] = []
        for s in sessions:
            prof = s.visitor_profile
            changes.append(
                DeltaEntityChange(
                    entity_type="VISITOR",
                    entity_id=s.id,
                    action="UPDATE" if s.created_at != s.updated_at else "CREATE",
                    payload={
                        "visitor_uuid": s.id,
                        "visitor_profile_id": s.visitor_profile_id,
                        "name": prof.name if prof else "Visitor",
                        "phone_number": prof.phone_number if prof else "",
                        "gender": prof.gender if prof else "MALE",
                        "age": prof.age if prof else 30,
                        "persons_count": s.persons_count,
                        "village_name_custom": prof.village_name_custom if prof else None,
                        "purpose_id": s.purpose_id,
                        "visitor_date": s.visit_date.isoformat(),
                        "visitor_time": s.check_in_time.isoformat(),
                        "status": s.status,
                        "notes": s.notes,
                        "sync_status": s.sync_status
                    },
                    server_synced_at=s.updated_at.isoformat() if s.updated_at else now_iso
                )
            )

        next_sync_token = f"token_{int(server_now.timestamp())}_{request.client_id[:8]}"

        return DeltaDownloadResponse(
            client_id=request.client_id,
            next_sync_token=next_sync_token,
            server_timestamp=now_iso,
            changes=changes,
            has_more=has_more
        )
