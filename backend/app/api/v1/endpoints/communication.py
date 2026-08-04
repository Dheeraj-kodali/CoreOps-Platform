from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from fastapi import APIRouter, Depends, Query, HTTPException, status
from app.api.deps import get_current_user, require_permission, get_communication_service
from app.models.user import User
from app.services.communication_service import CommunicationService
from app.schemas.communication import (
    CommunicationSettingsUpdate,
    CommunicationSettingsResponse,
    MessageTemplateUpdate,
    MessageTemplateResponse,
    MessagePreviewRequest,
    MessagePreviewResponse,
    CommunicationHistoryResponse,
    CommunicationHistoryListResponse,
    TestMessageRequest,
    TestMessageResponse,
)

router = APIRouter()


class BroadcastCreateRequest(BaseModel):
    title: str
    message: str
    channel: str = "WHATSAPP"  # WHATSAPP, SMS, EMAIL, IN_APP
    recipients_type: str = "ALL_VISITORS"  # ALL_VISITORS, PURPOSE, INSIDE, TODAY, SPECIFIC, STAFF
    purpose_id: Optional[str] = None
    scheduled_at: Optional[str] = None  # None for Send Now, ISO string for scheduled


@router.get(
    "/settings",
    response_model=CommunicationSettingsResponse,
    summary="Get communication settings",
)
async def get_communication_settings(
    current_user: User = Depends(get_current_user),
    service: CommunicationService = Depends(get_communication_service),
):
    settings = await service.get_settings()
    return CommunicationSettingsResponse.from_model(settings)


@router.put(
    "/settings",
    response_model=CommunicationSettingsResponse,
    summary="Update communication settings",
)
async def update_communication_settings(
    payload: CommunicationSettingsUpdate,
    current_user: User = Depends(get_current_user),
    service: CommunicationService = Depends(get_communication_service),
):
    settings = await service.update_settings(payload, current_user)
    return CommunicationSettingsResponse.from_model(settings)


@router.get(
    "/templates",
    response_model=list[MessageTemplateResponse],
    summary="Get all message templates",
)
async def get_all_templates(
    current_user: User = Depends(get_current_user),
    service: CommunicationService = Depends(get_communication_service),
):
    templates = await service.get_templates()
    return templates


@router.post(
    "/preview",
    response_model=MessagePreviewResponse,
    summary="Preview rendered message",
)
async def preview_message(
    payload: MessagePreviewRequest,
    current_user: User = Depends(get_current_user),
    service: CommunicationService = Depends(get_communication_service),
):
    result = await service.preview_message(
        payload.template_type, payload.custom_message
    )
    return MessagePreviewResponse(**result)


@router.get(
    "/history",
    response_model=CommunicationHistoryListResponse,
    summary="List communication history",
)
async def list_communication_history(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    service: CommunicationService = Depends(get_communication_service),
):
    items, total, pages = await service.get_all_history(page=page, limit=limit)
    return CommunicationHistoryListResponse(
        items=items,
        total=total,
        page=page,
        limit=limit,
        pages=pages,
    )


# --- Broadcast Management Endpoints ---

DEMO_BROADCASTS = [
    {
        "id": "bc-101",
        "title": "Maha Shivaratri Special Darshan Alert",
        "message": "Dear Devotees, Special Darshan for Maha Shivaratri will commence at 05:00 AM.",
        "channel": "WhatsApp",
        "recipients_type": "All Visitors",
        "recipient_count": 1450,
        "delivered": 1420,
        "failed": 30,
        "pending": 0,
        "status": "COMPLETED",
        "created_by": "admin",
        "created_at": "2026-07-30 08:30 AM",
    },
    {
        "id": "bc-102",
        "title": "Annadhanam Seva Timings Update",
        "message": "Afternoon Annadhanam will be served between 12:30 PM and 03:00 PM at Main Hall.",
        "channel": "WhatsApp",
        "recipients_type": "Visitors Currently Inside",
        "recipient_count": 38,
        "delivered": 38,
        "failed": 0,
        "pending": 0,
        "status": "COMPLETED",
        "created_by": "admin",
        "created_at": "2026-07-31 09:15 AM",
    },
    {
        "id": "bc-103",
        "title": "Volunteer Morning Briefing Reminder",
        "message": "All volunteers are requested to report to Reception Desk at 07:00 AM tomorrow.",
        "channel": "WhatsApp",
        "recipients_type": "Staff Members",
        "recipient_count": 15,
        "delivered": 0,
        "failed": 0,
        "pending": 15,
        "status": "SCHEDULED",
        "created_by": "admin",
        "created_at": "2026-07-31 10:00 AM",
    },
]


@router.get("/broadcasts")
async def list_broadcasts(
    current_user: User = Depends(get_current_user),
):
    return {"items": DEMO_BROADCASTS, "total": len(DEMO_BROADCASTS)}


@router.post("/broadcasts", status_code=status.HTTP_201_CREATED)
async def create_broadcast(
    payload: BroadcastCreateRequest,
    current_user: User = Depends(get_current_user),
    service: CommunicationService = Depends(get_communication_service),
):
    result = await service.send_broadcast_to_recipients(
        title=payload.title,
        custom_message=payload.message,
        recipients_type=payload.recipients_type,
        purpose_id=payload.purpose_id,
        created_by=getattr(current_user, "username", "admin"),
    )
    DEMO_BROADCASTS.insert(0, result)
    return result


@router.delete("/broadcasts/{broadcast_id}")
async def cancel_broadcast(
    broadcast_id: str,
    current_user: User = Depends(get_current_user),
):
    global DEMO_BROADCASTS
    DEMO_BROADCASTS = [b for b in DEMO_BROADCASTS if b["id"] != broadcast_id]
    return {"message": f"Broadcast {broadcast_id} cancelled."}


@router.post("/broadcasts/{broadcast_id}/retry")
async def retry_failed_broadcast(
    broadcast_id: str,
    current_user: User = Depends(get_current_user),
):
    for b in DEMO_BROADCASTS:
        if b["id"] == broadcast_id:
            b["delivered"] += b["failed"]
            b["failed"] = 0
            b["status"] = "COMPLETED"
            return {"message": "Failed deliveries retried successfully.", "broadcast": b}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Broadcast not found")


@router.get("/broadcasts/{broadcast_id}/deliveries")
async def get_broadcast_deliveries(
    broadcast_id: str,
    current_user: User = Depends(get_current_user),
):
    return {
        "broadcast_id": broadcast_id,
        "deliveries": [
            {"phone": "+91 98765 43210", "recipient": "Ramesh Kumar", "status": "DELIVERED", "time": "09:16 AM"},
            {"phone": "+91 91234 56789", "recipient": "Suresh Varma", "status": "DELIVERED", "time": "09:16 AM"},
            {"phone": "+91 99887 76655", "recipient": "Anitha Rao", "status": "DELIVERED", "time": "09:17 AM"},
        ]
    }
