from typing import Annotated
import gzip
import json
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User
from app.api.deps import get_current_user
from app.schemas.sync_v2 import (
    BatchUploadRequest, BatchUploadResponse,
    DeltaDownloadRequest, DeltaDownloadResponse
)
from app.services.sync_service_v2 import DeltaSyncServiceV2

router = APIRouter()


@router.post("/upload", response_model=BatchUploadResponse)
async def batch_upload_v2(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """v2 Delta Sync Batch Upload Endpoint.
    
    Receives batch outbox event payloads from edge client, validates SHA-256 checksums,
    executes idempotent deduplication, performs LWW conflict resolution, and records sync metrics.
    Supports Gzip compressed requests.
    """
    raw_body = await request.body()
    content_encoding = request.headers.get("content-encoding", "").lower()
    
    # Decompress Gzip if encoded
    if "gzip" in content_encoding:
        try:
            raw_body = gzip.decompress(raw_body)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid Gzip compressed payload: {str(e)}"
            )

    try:
        body_json = json.loads(raw_body.decode('utf-8'))
        upload_request = BatchUploadRequest(**body_json)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid JSON sync payload format: {str(e)}"
        )

    # Check X-Payload-SHA256 Header if provided
    header_sha256 = request.headers.get("x-payload-sha256")
    if header_sha256 and not upload_request.batch_sha256:
        upload_request.batch_sha256 = header_sha256

    # Active Temple Isolation Context
    upload_request.temple_id = getattr(request.state, "temple_id", "SKSA_MAIN")

    service = DeltaSyncServiceV2(db)
    response_data = await service.process_batch_upload(
        request=upload_request,
        current_user=current_user,
        payload_bytes_len=len(raw_body)
    )

    return response_data


@router.post("/download", response_model=DeltaDownloadResponse)
async def delta_download_v2(
    download_request: DeltaDownloadRequest,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """v2 Delta Sync Incremental Download Endpoint.
    
    Returns entity mutations updated on server since client's last_sync_token / since_timestamp.
    """
    temple_id = getattr(request.state, "temple_id", "SKSA_MAIN")
    service = DeltaSyncServiceV2(db)
    return await service.process_delta_download(
        request=download_request,
        temple_id=temple_id
    )
