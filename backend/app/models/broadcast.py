import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class BroadcastCampaign(BaseModel):
    __tablename__ = "broadcast_campaigns"

    campaign_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    temple_id = Column(String(36), ForeignKey("temples.id"), nullable=False, index=True)
    title = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    template_id = Column(String(50), nullable=True)
    message = Column(Text, nullable=False)
    status = Column(
        String(30), default="Draft", nullable=False, index=True
    )  # Draft, Validated, Approved, Queued, Sending, Completed, Cancelled, Failed, PartiallyCompleted

    audience_filter_json = Column(Text, nullable=True)

    created_by = Column(String(36), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    approved_at = Column(DateTime(timezone=True), nullable=True)
    scheduled_at = Column(DateTime(timezone=True), nullable=True, index=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)

    estimated_recipients = Column(Integer, default=0, nullable=False)
    total_recipients = Column(Integer, default=0, nullable=False)
    actual_recipients = Column(Integer, default=0, nullable=False)
    queued_count = Column(Integer, default=0, nullable=False)
    sent_count = Column(Integer, default=0, nullable=False)
    delivered_count = Column(Integer, default=0, nullable=False)
    failed_count = Column(Integer, default=0, nullable=False)
    cancelled_count = Column(Integer, default=0, nullable=False)
    retry_count = Column(Integer, default=0, nullable=False)

    recipients = relationship("BroadcastRecipient", back_populates="campaign", cascade="all, delete-orphan")

    @property
    def id(self) -> str:
        return self.campaign_id

    @id.setter
    def id(self, value: str) -> None:
        self.campaign_id = value


class BroadcastRecipient(BaseModel):
    __tablename__ = "broadcast_recipients"

    recipient_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    campaign_id = Column(String(36), ForeignKey("broadcast_campaigns.campaign_id"), nullable=False, index=True)
    temple_id = Column(String(36), nullable=False, default="SKSA_MAIN", index=True)
    person_id = Column(String(36), nullable=True, index=True)
    person_uuid = Column(String(36), nullable=True)
    phone_number = Column(String(20), nullable=False, default="", index=True)
    mobile_number = Column(String(20), nullable=False, default="", index=True)
    name = Column(String(100), nullable=True)
    status = Column(
        String(30), default="Queued", nullable=False, index=True
    )  # Queued, Sent, Delivered, Failed, Cancelled

    queued_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    failed_at = Column(DateTime(timezone=True), nullable=True)
    retry_count = Column(Integer, default=0, nullable=False)
    failure_reason = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)

    campaign = relationship("BroadcastCampaign", back_populates="recipients")
