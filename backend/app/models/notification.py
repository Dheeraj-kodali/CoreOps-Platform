from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class NotificationTemplate(BaseModel):
    __tablename__ = "notification_templates"

    code = Column(String(50), unique=True, nullable=False, index=True)
    channel = Column(String(20), nullable=False)  # SMS, WHATSAPP
    name = Column(String(100), nullable=False)
    content_en = Column(Text, nullable=False)
    content_te = Column(Text, nullable=False)

    notifications = relationship("Notification", back_populates="template")


class Notification(BaseModel):
    __tablename__ = "notifications"

    visitor_id = Column(String(36), ForeignKey("visitors.id"), nullable=True, index=True)
    template_id = Column(String(36), ForeignKey("notification_templates.id"), nullable=True, index=True)
    channel = Column(String(20), nullable=False)  # SMS, WHATSAPP
    content = Column(Text, nullable=False)
    status = Column(String(20), default="PENDING", nullable=False, index=True)  # PENDING, SENT, FAILED, DELIVERED

    visitor = relationship("Visitor", back_populates="notifications")
    template = relationship("NotificationTemplate", back_populates="notifications")


# Alias for backward compatibility
NotificationLog = Notification
