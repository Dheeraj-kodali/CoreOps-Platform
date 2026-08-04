from sqlalchemy import Column, String, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class CommunicationSetting(BaseModel):
    __tablename__ = "communication_settings"

    mode = Column(
        String(25),
        nullable=False,
        default="N8N_AUTOMATION",
        index=True,
    )  # MANUAL_WHATSAPP, META_CLOUD_API, N8N_AUTOMATION, DISABLED
    access_token = Column(Text, nullable=True)
    phone_number_id = Column(String(50), nullable=True)
    business_account_id = Column(String(50), nullable=True)
    verify_token = Column(String(100), nullable=True)
    n8n_webhook_url = Column(Text, nullable=True)
    auto_send = Column(Boolean, default=True, nullable=False)
    allow_edit = Column(Boolean, default=False, nullable=False)
    save_history = Column(Boolean, default=True, nullable=False)
    retry_failed = Column(Boolean, default=False, nullable=False)


class MessageTemplate(BaseModel):
    __tablename__ = "message_templates"

    template_type = Column(
        String(20),
        unique=True,
        nullable=False,
        index=True,
    )  # ENTRY, EXIT
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)


class CommunicationHistoryRecord(BaseModel):
    __tablename__ = "communication_history_v2"

    visitor_id = Column(
        String(36),
        ForeignKey("visitors.id"),
        nullable=True,
        index=True,
    )
    phone = Column(String(20), nullable=False, index=True)
    message = Column(Text, nullable=False)
    message_type = Column(
        String(20),
        nullable=False,
        index=True,
    )  # ENTRY, EXIT
    status = Column(
        String(20),
        default="PENDING",
        nullable=False,
        index=True,
    )  # PENDING, SENT, FAILED
    meta_message_id = Column(String(100), nullable=True)
    error_message = Column(Text, nullable=True)

    visitor = relationship("Visitor", backref="communication_records")
