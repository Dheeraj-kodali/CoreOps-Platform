from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class SyncQueue(BaseModel):
    __tablename__ = "sync_queue"

    temple_id = Column(String(36), ForeignKey("temples.id"), nullable=True, index=True)
    visitor_uuid = Column(String(36), nullable=False, index=True)
    client_id = Column(String(100), nullable=False)
    action_type = Column(String(20), nullable=False)  # CREATE, UPDATE, DELETE, CHECKOUT
    payload_json = Column(Text, nullable=False)
    status = Column(String(20), default="PENDING", nullable=False, index=True)  # PENDING, SYNCED, CONFLICT, FAILED
    error_message = Column(Text, nullable=True)
    client_timestamp = Column(DateTime(timezone=True), nullable=False)
    server_synced_at = Column(DateTime(timezone=True), nullable=True)


class SyncToken(BaseModel):
    __tablename__ = "sync_tokens"

    temple_id = Column(String(36), ForeignKey("temples.id"), nullable=False, index=True)
    client_id = Column(String(100), nullable=False, index=True)
    device_name = Column(String(100), nullable=True)
    last_synced_token = Column(String(100), nullable=True)
    last_synced_at = Column(DateTime(timezone=True), nullable=True)

    temple = relationship("Temple", backref="sync_tokens")
