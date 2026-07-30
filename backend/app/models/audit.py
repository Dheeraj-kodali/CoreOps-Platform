import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Float, DateTime, event, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.exceptions import ImmutableAuditException


def generate_uuid() -> str:
    return str(uuid.uuid4())


class AuditRecord(Base):
    """Enterprise-grade Immutable Audit Event Record (Append-only).
    
    Contains all 20 specification audit fields:
    - audit_id, trace_id, temple_id, user_id, role, device_id, session_id,
      action, entity_type, entity_id, old_value, new_value, status, severity,
      timestamp, ip_address, application_version, platform, api_version, duration_ms.
    """
    __tablename__ = "audit_logs"

    audit_id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    trace_id = Column(String(36), nullable=False, index=True, default=generate_uuid)
    temple_id = Column(String(36), nullable=False, index=True, default="SKSA_MAIN")
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)
    role = Column(String(50), nullable=True)
    device_id = Column(String(100), nullable=True)
    session_id = Column(String(100), nullable=True)

    action = Column(String(100), nullable=False, index=True)
    entity_type = Column(String(50), nullable=False, index=True)
    entity_id = Column(String(36), nullable=True, index=True)

    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)

    status = Column(String(20), default="SUCCESS", nullable=False, index=True)  # SUCCESS, FAILURE, DUPLICATE, CONFLICT
    severity = Column(String(20), default="INFO", nullable=False, index=True)  # INFO, WARNING, ERROR, CRITICAL

    timestamp = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )
    ip_address = Column(String(45), nullable=True)
    application_version = Column(String(20), default="2.0.0", nullable=False)
    platform = Column(String(50), default="Backend-FastAPI", nullable=False)
    api_version = Column(String(20), default="v2.0", nullable=False)
    duration_ms = Column(Float, default=0.0, nullable=False)

    user = relationship("User")

    @property
    def resource(self) -> str:
        return self.entity_type


# --- Immutability Enforcement Event Listeners ---

@event.listens_for(AuditRecord, "before_update")
def block_audit_update(mapper, connection, target):
    raise ImmutableAuditException("Audit records are immutable and append-only. UPDATE operations are strictly prohibited.")


@event.listens_for(AuditRecord, "before_delete")
def block_audit_delete(mapper, connection, target):
    raise ImmutableAuditException("Audit records are immutable and append-only. DELETE operations are strictly prohibited.")


# Model Alias for legacy imports
AuditLog = AuditRecord
