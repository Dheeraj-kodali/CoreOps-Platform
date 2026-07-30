from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class NotificationTemplateResponse(BaseModel):
    id: int
    code: str
    channel: str
    name: str
    content_en: str
    content_te: str

    model_config = ConfigDict(from_attributes=True)


class NotificationLogResponse(BaseModel):
    id: int
    visitor_id: Optional[int] = None
    phone_number: str
    channel: str
    template_id: Optional[int] = None
    message_content: str
    status: str
    retry_count: int
    last_retry_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NotificationLogListResponse(BaseModel):
    items: List[NotificationLogResponse]
    total: int
    page: int
    limit: int
    pages: int
