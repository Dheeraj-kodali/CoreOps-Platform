from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class SyncItem(BaseModel):
    visitor_uuid: str
    action_type: str = Field(..., pattern="^(CREATE|UPDATE|DELETE)$")
    payload: Dict[str, Any]
    client_timestamp: datetime


class BatchSyncRequest(BaseModel):
    client_id: str
    items: List[SyncItem]


class SyncItemResult(BaseModel):
    visitor_uuid: str
    status: str  # SYNCED, CONFLICT, FAILED
    error_message: Optional[str] = None
    server_synced_at: datetime


class BatchSyncResponse(BaseModel):
    processed: int
    success_count: int
    failure_count: int
    results: List[SyncItemResult]
