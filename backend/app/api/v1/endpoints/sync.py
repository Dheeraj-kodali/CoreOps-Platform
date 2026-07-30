from fastapi import APIRouter, Depends
from app.api.deps import get_current_user, get_sync_service
from app.models.user import User
from app.services.sync_service import SyncService
from app.schemas.sync import BatchSyncRequest, BatchSyncResponse

router = APIRouter()


@router.post("/batch", response_model=BatchSyncResponse)
async def batch_sync(
    request: BatchSyncRequest,
    service: SyncService = Depends(get_sync_service),
    current_user: User = Depends(get_current_user),
):
    return await service.process_batch_sync(request, current_user)
