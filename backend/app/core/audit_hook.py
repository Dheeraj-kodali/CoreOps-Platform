import json
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.audit import AuditRecord
from app.repositories.audit_repository import AuditRepository


async def record_audit_event(
    db: AsyncSession,
    action: str,
    **kwargs: Any
) -> AuditRecord:
    """Standardized Backend Audit Hook Interceptor.
    
    Emits structured, immutable AuditRecord instances across backend operations.
    Accepts explicit or keyword parameters to comply with parameter limit lint rules.
    """
    entity_type = kwargs.get("entity_type", "SYSTEM")
    resource = kwargs.get("resource")
    resolved_entity_type = resource if (resource and (entity_type == "SYSTEM" or not entity_type)) else (entity_type or "SYSTEM")

    entity_id = kwargs.get("entity_id")
    affected_record_id = kwargs.get("affected_record_id")
    resolved_entity_id = entity_id or affected_record_id

    result = kwargs.get("result", "SUCCESS")
    status = kwargs.get("status")
    resolved_status = status or result or "SUCCESS"

    old_val = kwargs.get("old_value")
    new_val = kwargs.get("new_value")
    reason = kwargs.get("reason")

    repo = AuditRepository(db)
    return await repo.create(
        action=action,
        entity_type=resolved_entity_type,
        entity_id=resolved_entity_id,
        trace_id=kwargs.get("trace_id"),
        user_id=kwargs.get("user_id"),
        temple_id=kwargs.get("temple_id", "SKSA_MAIN"),
        role=kwargs.get("role"),
        device_id=kwargs.get("device_id"),
        session_id=kwargs.get("session_id"),
        old_value=json.dumps(old_val) if isinstance(old_val, dict) else old_val,
        new_value=json.dumps(new_val) if isinstance(new_val, dict) else (new_val or reason),
        status=resolved_status,
        severity=kwargs.get("severity", "INFO"),
        ip_address=kwargs.get("ip_address"),
        application_version=kwargs.get("application_version", "2.0.0"),
        platform=kwargs.get("platform", "Backend-FastAPI"),
        api_version=kwargs.get("api_version", "v2.0"),
        duration_ms=kwargs.get("duration_ms", 0.0),
    )

