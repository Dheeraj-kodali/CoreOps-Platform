from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class SMSLog(BaseModel):
    __tablename__ = "sms_logs"

    phone_number = Column(String(20), nullable=False, index=True)
    message_content = Column(Text, nullable=False)
    provider_response = Column(Text, nullable=True)
    status = Column(String(20), default="PENDING", nullable=False, index=True)  # PENDING, SENT, FAILED
    retry_count = Column(Integer, default=0, nullable=False)
    last_retry_at = Column(DateTime(timezone=True), nullable=True)


class WhatsAppLog(BaseModel):
    __tablename__ = "whatsapp_logs"

    phone_number = Column(String(20), nullable=False, index=True)
    message_content = Column(Text, nullable=False)
    provider_response = Column(Text, nullable=True)
    status = Column(String(20), default="PENDING", nullable=False, index=True)  # PENDING, SENT, FAILED
    retry_count = Column(Integer, default=0, nullable=False)
    last_retry_at = Column(DateTime(timezone=True), nullable=True)


class Report(BaseModel):
    __tablename__ = "reports"

    report_type = Column(String(50), nullable=False, index=True)  # DAILY, WEEKLY, MONTHLY, VOLUNTEER
    title = Column(String(200), nullable=False)
    generated_by = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    file_url = Column(String(500), nullable=True)
    format = Column(String(10), nullable=False)  # pdf, excel, csv
    parameters_json = Column(Text, nullable=True)

    user = relationship("User")
