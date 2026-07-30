from datetime import datetime, timezone
import json
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.base_service import BaseService
from app.repositories.visitor_repository import VisitorRepository
from app.models.sync import SyncQueue
from app.models.user import User
from app.schemas.sync import BatchSyncRequest, BatchSyncResponse, SyncItemResult


class SyncService(BaseService[SyncQueue]):
    """
    Domain Service for Ingesting Offline Batch Operations, Managing Sync Audit Queues,
    and Executing Idempotent Conflict Resolution.
    """

    def __init__(self, db_session: AsyncSession):
        super().__init__(db_session)
        self.visitor_repo = VisitorRepository(db_session)

    async def process_batch_sync(self, request: BatchSyncRequest, current_user: User) -> BatchSyncResponse:
        results = []
        success_count = 0
        failure_count = 0

        for item in request.items:
            sync_time = datetime.now(timezone.utc)
            try:
                # Insert persistent audit log entry for sync attempt
                queue_entry = SyncQueue(
                    visitor_uuid=item.visitor_uuid,
                    client_id=request.client_id,
                    action_type=item.action_type,
                    payload_json=json.dumps(item.payload, default=str),
                    status="PENDING",
                    client_timestamp=item.client_timestamp,
                )
                self.db.add(queue_entry)

                if item.action_type == "CREATE":
                    existing = await self.visitor_repo.get_by_uuid(item.visitor_uuid)
                    if existing:
                        # Idempotent skip if record already exists
                        queue_entry.status = "SYNCED"
                        queue_entry.server_synced_at = sync_time
                        success_count += 1
                        results.append(
                            SyncItemResult(
                                visitor_uuid=item.visitor_uuid,
                                status="SYNCED",
                                server_synced_at=sync_time,
                            )
                        )
                        continue

                    payload_data = dict(item.payload)
                    payload_data["visitor_uuid"] = item.visitor_uuid
                    payload_data["volunteer_id"] = current_user.id
                    payload_data["sync_status"] = "SYNCED"

                    await self.visitor_repo.create(payload_data, user_id=current_user.id)
                    queue_entry.status = "SYNCED"
                    queue_entry.server_synced_at = sync_time
                    success_count += 1

                    results.append(
                        SyncItemResult(
                            visitor_uuid=item.visitor_uuid,
                            status="SYNCED",
                            server_synced_at=sync_time,
                        )
                    )

                elif item.action_type == "UPDATE":
                    existing = await self.visitor_repo.get_by_uuid(item.visitor_uuid)
                    if not existing:
                        # Conflict handling: target server record missing
                        queue_entry.status = "CONFLICT"
                        queue_entry.error_message = "Target record not found on server for update"
                        failure_count += 1
                        results.append(
                            SyncItemResult(
                                visitor_uuid=item.visitor_uuid,
                                status="CONFLICT",
                                error_message="Target record not found on server for update",
                                server_synced_at=sync_time,
                            )
                        )
                    else:
                        await self.visitor_repo.update(existing, item.payload, user_id=current_user.id)
                        queue_entry.status = "SYNCED"
                        queue_entry.server_synced_at = sync_time
                        success_count += 1
                        results.append(
                            SyncItemResult(
                                visitor_uuid=item.visitor_uuid,
                                status="SYNCED",
                                server_synced_at=sync_time,
                            )
                        )

            except Exception as e:
                failure_count += 1
                results.append(
                    SyncItemResult(
                        visitor_uuid=item.visitor_uuid,
                        status="FAILED",
                        error_message=str(e),
                        server_synced_at=sync_time,
                    )
                )

        await self.commit()
        return BatchSyncResponse(
            processed=len(request.items),
            success_count=success_count,
            failure_count=failure_count,
            results=results,
        )
