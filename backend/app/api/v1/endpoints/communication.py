from fastapi import APIRouter, Depends, Query
from app.api.deps import require_permission, get_communication_service
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


@router.get(
    "/settings",
    response_model=CommunicationSettingsResponse,
    summary="Get communication settings",
)
async def get_communication_settings(
    current_user: User = Depends(require_permission("MANAGE_SETTINGS")),
    service: CommunicationService = Depends(get_communication_service),
):
    """Retrieve current communication settings including mode and behavior flags."""
    settings = await service.get_settings()
    return CommunicationSettingsResponse.from_model(settings)


@router.put(
    "/settings",
    response_model=CommunicationSettingsResponse,
    summary="Update communication settings",
)
async def update_communication_settings(
    payload: CommunicationSettingsUpdate,
    current_user: User = Depends(require_permission("MANAGE_SETTINGS")),
    service: CommunicationService = Depends(get_communication_service),
):
    """Update communication mode, API credentials, and behavior flags."""
    settings = await service.update_settings(payload, current_user)
    return CommunicationSettingsResponse.from_model(settings)


@router.get(
    "/templates",
    response_model=list[MessageTemplateResponse],
    summary="Get all message templates",
)
async def get_all_templates(
    current_user: User = Depends(require_permission("MANAGE_SETTINGS")),
    service: CommunicationService = Depends(get_communication_service),
):
    """Retrieve all message templates (ENTRY and EXIT)."""
    templates = await service.get_templates()
    return templates


@router.get(
    "/templates/{template_type}",
    response_model=MessageTemplateResponse,
    summary="Get template by type",
)
async def get_template_by_type(
    template_type: str,
    current_user: User = Depends(require_permission("MANAGE_SETTINGS")),
    service: CommunicationService = Depends(get_communication_service),
):
    """Retrieve a specific message template by type (ENTRY or EXIT)."""
    template = await service.get_template_by_type(template_type.upper())
    if not template:
        from app.core.exceptions import EntityNotFoundException
        raise EntityNotFoundException("MessageTemplate", template_type)
    return template


@router.put(
    "/templates/{template_type}",
    response_model=MessageTemplateResponse,
    summary="Update template by type",
)
async def update_template(
    template_type: str,
    payload: MessageTemplateUpdate,
    current_user: User = Depends(require_permission("MANAGE_SETTINGS")),
    service: CommunicationService = Depends(get_communication_service),
):
    """Create or update a message template for the specified type (ENTRY or EXIT)."""
    template = await service.update_template(
        template_type.upper(), payload, current_user
    )
    return template


@router.post(
    "/preview",
    response_model=MessagePreviewResponse,
    summary="Preview rendered message",
)
async def preview_message(
    payload: MessagePreviewRequest,
    current_user: User = Depends(require_permission("MANAGE_SETTINGS")),
    service: CommunicationService = Depends(get_communication_service),
):
    """Render a message template with sample data for preview."""
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
    current_user: User = Depends(require_permission("MANAGE_SETTINGS")),
    service: CommunicationService = Depends(get_communication_service),
):
    """Retrieve paginated communication dispatch history."""
    items, total, pages = await service.get_all_history(page=page, limit=limit)
    return CommunicationHistoryListResponse(
        items=items,
        total=total,
        page=page,
        limit=limit,
        pages=pages,
    )


@router.get(
    "/history/{visitor_id}",
    response_model=list[CommunicationHistoryResponse],
    summary="Get history for visitor",
)
async def get_visitor_communication_history(
    visitor_id: str,
    current_user: User = Depends(require_permission("MANAGE_SETTINGS")),
    service: CommunicationService = Depends(get_communication_service),
):
    """Retrieve all communication history records for a specific visitor."""
    records = await service.get_history_for_visitor(visitor_id)
    return records


@router.post(
    "/test",
    response_model=TestMessageResponse,
    summary="Send test WhatsApp message",
)
async def send_test_whatsapp_message(
    payload: TestMessageRequest,
    current_user: User = Depends(require_permission("MANAGE_SETTINGS")),
    service: CommunicationService = Depends(get_communication_service),
):
    """Dispatch a test WhatsApp message using current Meta Cloud API credentials stored in settings."""
    result = await service.send_test_message(
        recipient_phone=payload.recipient_phone,
        template_type=payload.template_type,
        custom_message=payload.custom_message,
    )
    return TestMessageResponse(**result)
