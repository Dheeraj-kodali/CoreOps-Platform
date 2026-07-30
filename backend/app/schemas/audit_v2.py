from typing import List, Optional
from pydantic import BaseModel, Field


class AuditRecordItem(BaseModel):
    audit_id: str
    trace_id: str
    temple_id: str
    user_id: Optional[str] = None
    role: Optional[str] = None
    device_id: Optional[str] = None
    session_id: Optional[str] = None
    action: str
    entity_type: str
    entity_id: Optional[str] = None
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    status: str
    severity: str
    timestamp: str
    ip_address: Optional[str] = None
    application_version: str
    platform: str
    api_version: str
    duration_ms: float


class AuditSearchRequest(BaseModel):
    temple_id: Optional[str] = "SKSA_MAIN"
    action: Optional[str] = None
    severity: Optional[str] = None  # INFO, WARNING, ERROR, CRITICAL
    entity_type: Optional[str] = None
    user_id: Optional[str] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    page: int = 1
    page_size: int = 50


class AuditSearchResponse(BaseModel):
    items: List[AuditRecordItem]
    total_count: int
    page: int
    page_size: int
    total_pages: int


class AuditExportRequest(BaseModel):
    temple_id: Optional[str] = "SKSA_MAIN"
    action: Optional[str] = None
    severity: Optional[str] = None
    entity_type: Optional[str] = None
    user_id: Optional[str] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    format: str = Field("json", description="Export format: json or csv")
