import json
import time
import hashlib
from datetime import datetime, timezone
from typing import List, Tuple, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_

from app.models.sync import SyncQueue, SyncToken
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

        # Emit SYNC_START Audit Event
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

        # Validate Batch-level SHA-256 Checksum if provided
        if request.batch_sha256:
            raw_payload_str = json.dumps([e.dict() for e in request.events], sort_keys=True)
            calculated_hash = hashlib.sha256(raw_payload_str.encode('utf-8')).hexdigest()
            if calculated_hash.lower() != request.batch_sha256.lower():
                # Batch integrity failure
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

        # Process each outbox event item
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

        # Generate Next Sync Sequence Token
        now_utc = datetime.now(timezone.utc)
        next_sync_token = f"token_{int(now_utc.timestamp())}_{request.client_id[:8]}"

        # Upsert Sync Token state for Client Device
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

        # 1. SHA-256 Payload Hash Check if provided
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

        # 2. Idempotency Check: Query duplicate event in SyncQueue by event_id
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

        # Record outbox sync attempt in SyncQueue
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
            # 3. Action Execution & LWW Conflict Resolution
            if event.action == "CREATE":
                if event.entity_type == "VISITOR":
                    v_res = await self.db.execute(
                        select(Visitor).filter(Visitor.visitor_uuid == event.entity_id)
                    )
                    existing_visitor = v_res.scalars().first()
                    if existing_visitor:
                        queue_record.status = "DUPLICATE"
                        return SyncItemResponse(
                            event_id=event.event_id,
                            entity_id=event.entity_id,
                            status="DUPLICATE",
                            retryable=False,
                            server_synced_at=now_iso
                        ), "DUPLICATE"

                    p = event.payload
                    new_visitor = Visitor(
                        visitor_uuid=event.entity_id,
                        temple_id=temple_id,
                        name=p.get("name", "Unknown Visitor"),
                        phone_number=p.get("phone_number", p.get("phone", "+910000000000")),
                        gender=p.get("gender", "OTHER"),
                        age=int(p.get("age", 30)),
                        persons_count=int(p.get("persons_count", p.get("personsCount", 1))),
                        village_name_custom=p.get("village", p.get("village_name_custom")),
                        purpose_id=p.get("purpose_id", p.get("purposeId", "default_purpose")),
                        temple_service=p.get("temple_service", p.get("purpose")),
                        visitor_date=datetime.strptime(p.get("visitor_date", p.get("date", "2026-07-30")), "%Y-%m-%d").date(),
                        visitor_time=datetime.strptime(p.get("visitor_time", p.get("time_in", "10:00:00")), "%H:%M:%S").time(),
                        volunteer_id=user_id,
                        notes=p.get("notes"),
                        sync_status="SYNCED"
                    )
                    self.db.add(new_visitor)
                    queue_record.status = "SYNCED"
                    return SyncItemResponse(
                        event_id=event.event_id,
                        entity_id=event.entity_id,
                        status="SYNCED",
                        retryable=False,
                        server_synced_at=now_iso
                    ), "SYNCED"

                elif event.entity_type == "PERSON":
                    p_res = await self.db.execute(select(Person).filter(Person.id == event.entity_id))
                    if p_res.scalars().first():
                        queue_record.status = "DUPLICATE"
                        return SyncItemResponse(
                            event_id=event.event_id,
                            entity_id=event.entity_id,
                            status="DUPLICATE",
                            retryable=False,
                            server_synced_at=now_iso
                        ), "DUPLICATE"

                    p = event.payload
                    new_person = Person(
                        id=event.entity_id,
                        temple_id=temple_id,
                        name=p.get("name"),
                        phone=p.get("phone"),
                        village=p.get("village"),
                        address=p.get("address"),
                        first_visit=p.get("first_visit", now_iso),
                        last_visit=p.get("last_visit", now_iso),
                        total_visits=int(p.get("total_visits", 1))
                    )
                    self.db.add(new_person)
                    queue_record.status = "SYNCED"
                    return SyncItemResponse(
                        event_id=event.event_id,
                        entity_id=event.entity_id,
                        status="SYNCED",
                        retryable=False,
                        server_synced_at=now_iso
                    ), "SYNCED"

            elif event.action in ("UPDATE", "CHECKOUT"):
                v_res = await self.db.execute(
                    select(Visitor).filter(Visitor.visitor_uuid == event.entity_id)
                )
                existing_visitor = v_res.scalars().first()
                if not existing_visitor:
                    queue_record.status = "CONFLICT"
                    queue_record.error_message = "Target record not found on server for update"
                    return SyncItemResponse(
                        event_id=event.event_id,
                        entity_id=event.entity_id,
                        status="CONFLICT",
                        retryable=False,
                        error_message="Target record not found on server for update",
                        server_synced_at=now_iso
                    ), "CONFLICT"

                # LWW Conflict Evaluation: Compare Client Timestamp with Existing Record updated_at
                client_dt = datetime.fromisoformat(event.client_timestamp.replace("Z", "+00:00"))
                updated_at = existing_visitor.updated_at
                if updated_at:
                    if updated_at.tzinfo is None:
                        updated_at = updated_at.replace(tzinfo=timezone.utc)
                    if client_dt < updated_at:
                        queue_record.status = "CONFLICT"
                        queue_record.error_message = "Server record has newer timestamp (LWW Conflict)"
                        return SyncItemResponse(
                            event_id=event.event_id,
                            entity_id=event.entity_id,
                            status="CONFLICT",
                            retryable=False,
                            error_message="Server record has newer timestamp (LWW Conflict)",
                            server_synced_at=now_iso
                        ), "CONFLICT"

                # Apply Update / Checkout
                p = event.payload
                if event.action == "CHECKOUT":
                    time_out_str = p.get("time_out", p.get("timeOut", "18:00:00"))
                    existing_visitor.notes = (existing_visitor.notes or "") + f" | Checked out at {time_out_str}"
                else:
                    if "notes" in p:
                        existing_visitor.notes = p["notes"]

                existing_visitor.sync_status = "SYNCED"
                queue_record.status = "SYNCED"
                return SyncItemResponse(
                    event_id=event.event_id,
                    entity_id=event.entity_id,
                    status="SYNCED",
                    retryable=False,
                    server_synced_at=now_iso
                ), "SYNCED"

            # Unknown Action or Entity Fallback
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

        # Parse threshold timestamp
        threshold_dt: Optional[datetime] = None
        if request.since_timestamp:
            try:
                threshold_dt = datetime.fromisoformat(request.since_timestamp.replace("Z", "+00:00"))
            except ValueError:
                threshold_dt = None

        query = select(Visitor).filter(
            or_(Visitor.temple_id == temple_id, Visitor.temple_id.is_(None)),
            Visitor.is_deleted.is_(False)
        )
        if threshold_dt:
            query = query.filter(Visitor.updated_at >= threshold_dt)

        query = query.order_by(Visitor.updated_at.asc()).limit(request.limit + 1)
        res = await self.db.execute(query)
        visitors = res.scalars().all()

        has_more = len(visitors) > request.limit
        if has_more:
            visitors = visitors[:request.limit]

        changes: List[DeltaEntityChange] = []
        for v in visitors:
            changes.append(
                DeltaEntityChange(
                    entity_type="VISITOR",
                    entity_id=v.visitor_uuid,
                    action="UPDATE" if v.created_at != v.updated_at else "CREATE",
                    payload={
                        "visitor_uuid": v.visitor_uuid,
                        "name": v.name,
                        "phone_number": v.phone_number,
                        "gender": v.gender,
                        "age": v.age,
                        "persons_count": v.persons_count,
                        "village_name_custom": v.village_name_custom,
                        "purpose_id": v.purpose_id,
                        "temple_service": v.temple_service,
                        "visitor_date": v.visitor_date.isoformat(),
                        "visitor_time": v.visitor_time.isoformat(),
                        "notes": v.notes,
                        "sync_status": v.sync_status
                    },
                    server_synced_at=v.updated_at.isoformat() if v.updated_at else now_iso
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
