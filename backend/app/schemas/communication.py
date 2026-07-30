from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class CommunicationSettingsUpdate(BaseModel):
    mode: str = Field(
        ...,
        pattern="^(MANUAL_WHATSAPP|META_CLOUD_API|DISABLED)$",
        description="Communication mode",
    )
    access_token: Optional[str] = None
    phone_number_id: Optional[str] = None
    business_account_id: Optional[str] = None
    verify_token: Optional[str] = None
    auto_send: bool = False
    allow_edit: bool = False
    save_history: bool = True
    retry_failed: bool = False


class CommunicationSettingsResponse(BaseModel):
    id: str
    mode: str
    access_token_masked: str = Field(
        default="",
        description="Access token masked for security — only last 6 chars shown",
    )
    phone_number_id: Optional[str] = None
    business_account_id: Optional[str] = None
    verify_token: Optional[str] = None
    auto_send: bool
    allow_edit: bool
    save_history: bool
    retry_failed: bool
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_model(cls, obj) -> "CommunicationSettingsResponse":
        token = obj.access_token or ""
        masked = f"***{token[-6:]}" if len(token) > 6 else "***" if token else ""
        return cls(
            id=obj.id,
            mode=obj.mode,
            access_token_masked=masked,
            phone_number_id=obj.phone_number_id,
            business_account_id=obj.business_account_id,
            verify_token=obj.verify_token,
            auto_send=obj.auto_send,
            allow_edit=obj.allow_edit,
            save_history=obj.save_history,
            retry_failed=obj.retry_failed,
            updated_at=obj.updated_at,
        )


class MessageTemplateUpdate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1)


class MessageTemplateResponse(BaseModel):
    id: str
    template_type: str
    title: str
    message: str
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MessagePreviewRequest(BaseModel):
    template_type: str = Field(..., pattern="^(ENTRY|EXIT)$")
    custom_message: Optional[str] = Field(
        None,
        description="Optional custom message override. If omitted, uses stored template.",
    )


class MessagePreviewResponse(BaseModel):
    template_type: str
    original_template: str
    rendered_message: str
    placeholders_used: List[str]


class CommunicationHistoryResponse(BaseModel):
    id: str
    visitor_id: Optional[str] = None
    phone: str
    message: str
    message_type: str
    status: str
    meta_message_id: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CommunicationHistoryListResponse(BaseModel):
    items: List[CommunicationHistoryResponse]
    total: int
    page: int
    limit: int
    pages: int


class TestMessageRequest(BaseModel):
    recipient_phone: str = Field(..., description="Target phone number for live test dispatch")
    template_type: str = Field("ENTRY", pattern="^(ENTRY|EXIT)$")
    custom_message: Optional[str] = Field(None, description="Optional custom text override")


class TestMessageResponse(BaseModel):
    success: bool
    status: str  # SENT, FAILED
    meta_message_id: Optional[str] = None
    error_message: Optional[str] = None
    http_status: Optional[int] = None
    rendered_message: str

