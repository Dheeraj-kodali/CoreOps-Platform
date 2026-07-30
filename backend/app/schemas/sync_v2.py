from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class SyncEventItem(BaseModel):
    event_id: str = Field(..., description="Client-generated unique event UUID v4")
    entity_type: str = Field(..., description="Target entity type: VISITOR, PERSON, CHECKOUT")
    entity_id: str = Field(..., description="Target entity primary UUID")
    action: str = Field(..., description="Mutation action: CREATE, UPDATE, DELETE, CHECKOUT")
    payload: Dict[str, Any] = Field(..., description="JSON payload data")
    client_timestamp: str = Field(..., description="ISO 8601 UTC client event creation timestamp")
    sha256_hash: Optional[str] = Field(None, description="SHA-256 integrity hash of payload string")


class BatchUploadRequest(BaseModel):
    client_id: str = Field(..., description="Client device identifier")
    temple_id: Optional[str] = Field("SKSA_MAIN", description="Tenant temple ID")
    last_sync_token: Optional[str] = Field(None, description="Client's last known sync token")
    batch_sha256: Optional[str] = Field(None, description="SHA-256 checksum of entire batch events array")
    events: List[SyncEventItem] = Field(..., description="List of outbox sync events to process")


class SyncItemResponse(BaseModel):
    event_id: str
    entity_id: str
    status: str  # SYNCED, DUPLICATE, CONFLICT, FAILED
    retryable: bool = False
    error_message: Optional[str] = None
    server_synced_at: str


class SyncMetrics(BaseModel):
    latency_ms: float
    items_processed: int
    success_count: int
    duplicates_count: int
    conflicts_count: int
    failed_count: int
    payload_size_bytes: int


class BatchUploadResponse(BaseModel):
    client_id: str
    next_sync_token: str
    results: List[SyncItemResponse]
    metrics: SyncMetrics


class DeltaDownloadRequest(BaseModel):
    client_id: str
    last_sync_token: Optional[str] = None
    since_timestamp: Optional[str] = None
    limit: int = 500


class DeltaEntityChange(BaseModel):
    entity_type: str
    entity_id: str
    action: str
    payload: Dict[str, Any]
    server_synced_at: str


class DeltaDownloadResponse(BaseModel):
    client_id: str
    next_sync_token: str
    server_timestamp: str
    changes: List[DeltaEntityChange]
    has_more: bool = False
