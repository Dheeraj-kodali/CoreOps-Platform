from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class AudienceFilterSpec(BaseModel):
    filter_type: str = Field(
        ...,
        description="Filter type: ALL_DEVOTEES, LAST_7_DAYS, LAST_30_DAYS, LAST_90_DAYS, CUSTOM_DATE_RANGE, VILLAGE, PURPOSE, REPEAT_VISITORS, FIRST_TIME_VISITORS, VIP, VOLUNTEERS, CUSTOM_SELECTION"
    )
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    village: Optional[str] = None
    purpose: Optional[str] = None
    custom_person_uuids: Optional[List[str]] = None


class AudienceCountRequest(BaseModel):
    temple_id: Optional[str] = "SKSA_MAIN"
    audience_filter: AudienceFilterSpec


class AudienceCountResponse(BaseModel):
    estimated_recipients_count: int
    audience_summary: str


class BroadcastPreviewRequest(BaseModel):
    temple_id: Optional[str] = "SKSA_MAIN"
    title: str
    message: str
    audience_filter: AudienceFilterSpec


class BroadcastPreviewResponse(BaseModel):
    campaign_name: str
    audience_size: int
    estimated_whatsapp_messages: int
    estimated_duration_seconds: float
    message_preview: str
    confirmation_required: bool = True


class BroadcastCampaignCreateRequest(BaseModel):
    temple_id: Optional[str] = "SKSA_MAIN"
    title: str
    description: Optional[str] = None
    template_id: Optional[str] = None
    message: str
    audience_filter: AudienceFilterSpec
    scheduled_at: Optional[str] = None  # ISO format string or None for Send Now
    confirmed: bool = Field(False, description="Explicit user confirmation safety rule")


class BroadcastRecipientItem(BaseModel):
    recipient_id: str
    campaign_id: str
    mobile_number: str
    name: Optional[str] = None
    status: str
    sent_at: Optional[str] = None
    delivered_at: Optional[str] = None
    failed_at: Optional[str] = None
    retry_count: int
    error_message: Optional[str] = None


class BroadcastCampaignDetailResponse(BaseModel):
    campaign_id: str
    temple_id: str
    title: str
    description: Optional[str] = None
    template_id: Optional[str] = None
    message: str
    status: str
    created_by: Optional[str] = None
    created_at: str
    scheduled_at: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    total_recipients: int
    queued_count: int
    sent_count: int
    delivered_count: int
    failed_count: int
    cancelled_count: int
    recipients_sample: Optional[List[BroadcastRecipientItem]] = None


class BroadcastAnalyticsResponse(BaseModel):
    total_campaigns: int
    total_messages_sent: int
    delivery_rate_percentage: float
    failure_rate_percentage: float
    average_delivery_time_seconds: float
    most_used_templates: List[Dict[str, Any]]
    most_common_audiences: List[Dict[str, Any]]


class BroadcastTemplateItem(BaseModel):
    template_id: str
    category: str  # Festival, Annadanam, Special Pooja, Temple Closed, Donation Drive, Emergency, Custom
    title: str
    body_template: str
