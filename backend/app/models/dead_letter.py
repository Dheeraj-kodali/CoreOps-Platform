import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Integer, DateTime
from app.models.base import BaseModel


class DeadLetterJob(BaseModel):
    """ORM Model for tracking permanently failed broadcast or sync jobs."""

    __tablename__ = "dead_letter_jobs"

    job_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_type = Column(String(50), nullable=False, index=True)  # BROADCAST_DISPATCH, SYNC_EVENT, BACKGROUND_TASK
    entity_id = Column(String(36), nullable=False, index=True)
    temple_id = Column(String(36), nullable=False, default="SKSA_MAIN", index=True)
    payload_json = Column(Text, nullable=True)
    failure_reason = Column(Text, nullable=False)
    stack_trace = Column(Text, nullable=True)
    attempts_count = Column(Integer, default=1, nullable=False)
    status = Column(String(20), default="UNRESOLVED", nullable=False, index=True)  # UNRESOLVED, REPROCESSED, DISCARDED

    failed_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    reprocessed_at = Column(DateTime(timezone=True), nullable=True)
    reprocessed_by = Column(String(36), nullable=True)
