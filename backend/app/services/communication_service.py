import logging
from typing import Optional, List, Tuple
from math import ceil
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.base_service import BaseService
from app.services.template_engine import TemplateEngine
from app.services.meta_whatsapp_service import MetaWhatsAppService
from app.services.n8n_whatsapp_service import N8NWhatsAppService
from app.repositories.communication_repository import CommunicationRepository
from app.repositories.message_template_repository import MessageTemplateRepository
from app.repositories.message_history_repository import MessageHistoryRepository
from app.models.communication import (
    CommunicationSetting,
    MessageTemplate,
    CommunicationHistoryRecord,
)
from app.models.user import User
from app.schemas.communication import (
    CommunicationSettingsUpdate,
    MessageTemplateUpdate,
)

logger = logging.getLogger(__name__)


class CommunicationService(BaseService):
    """
    Domain service orchestrating communication settings, template management,
    message rendering, and dispatch history.
    """

    def __init__(self, db_session: AsyncSession):
        super().__init__(db_session)
        self.comm_repo = CommunicationRepository(db_session)
        self.template_repo = MessageTemplateRepository(db_session)
        self.history_repo = MessageHistoryRepository(db_session)
        self.engine = TemplateEngine()

    # ── Settings ──────────────────────────────────────────────

    async def get_settings(self) -> CommunicationSetting:
        """Retrieve communication settings, creating defaults if none exist."""
        return await self.comm_repo.get_or_create_settings()

    async def update_settings(
        self, payload: CommunicationSettingsUpdate, current_user: User
    ) -> CommunicationSetting:
        """Update communication settings."""
        data = payload.model_dump(exclude_unset=True)
        settings = await self.comm_repo.update_settings(
            data, user_id=current_user.id
        )
        await self.commit()
        return settings

    # ── Templates ─────────────────────────────────────────────

    async def get_templates(self) -> List[MessageTemplate]:
        """Retrieve all message templates."""
        return await self.template_repo.get_all_templates()

    async def get_template_by_type(
        self, template_type: str
    ) -> Optional[MessageTemplate]:
        """Retrieve a specific template by type (ENTRY or EXIT)."""
        return await self.template_repo.get_by_type(template_type)

    async def update_template(
        self,
        template_type: str,
        payload: MessageTemplateUpdate,
        current_user: User,
    ) -> MessageTemplate:
        """Create or update a message template for the given type."""
        data = payload.model_dump()
        template = await self.template_repo.upsert_template(
            template_type, data, user_id=current_user.id
        )
        await self.commit()
        return template

    # ── Preview ───────────────────────────────────────────────

    async def preview_message(
        self, template_type: str, custom_message: Optional[str] = None
    ) -> dict:
        """
        Render a template with sample data for admin preview.
        Optionally accepts a custom message override instead of the stored template.
        """
        if custom_message:
            template_text = custom_message
        else:
            template = await self.template_repo.get_by_type(template_type)
            if not template:
                template_text = f"No {template_type} template configured."
            else:
                template_text = template.message

        rendered = self.engine.preview(template_text)
        placeholders = self.engine.extract_placeholders(template_text)

        return {
            "template_type": template_type,
            "original_template": template_text,
            "rendered_message": rendered,
            "placeholders_used": placeholders,
        }

    # ── History ───────────────────────────────────────────────

    async def get_history_for_visitor(
        self, visitor_id: str
    ) -> List[CommunicationHistoryRecord]:
        """Get all communication history records for a specific visitor."""
        return await self.history_repo.get_by_visitor(visitor_id)

    async def get_all_history(
        self, page: int = 1, limit: int = 20
    ) -> Tuple[List[CommunicationHistoryRecord], int, int]:
        """Get paginated communication history."""
        items, total = await self.history_repo.get_paginated(
            page=page, limit=limit
        )
        pages = ceil(total / limit) if total > 0 else 1
        return items, total, pages

    # ── Message Dispatch Orchestration ────────────────────────

    async def prepare_and_record_message(
        self,
        visitor_id: str,
        phone: str,
        message_type: str,
        context: dict,
    ) -> Optional[CommunicationHistoryRecord]:
        """
        Full message lifecycle:
        1. Load settings to determine mode
        2. Load and render the template
        3. Dispatch via the appropriate provider
        4. Record the result in communication history
        """
        settings = await self.get_settings()

        if settings.mode == "DISABLED":
            logger.info("Communication is DISABLED — skipping message dispatch")
            return None

        template = await self.template_repo.get_by_type(message_type)
        if not template:
            logger.warning(f"No template found for type: {message_type}")
            return None

        rendered_message = self.engine.render(template.message, context)

        history_data = {
            "visitor_id": None,
            "phone": phone,
            "message": rendered_message,
            "message_type": message_type,
            "status": "PENDING",
            "meta_message_id": None,
            "error_message": None,
        }

        if settings.mode == "N8N_AUTOMATION":
            n8n_service = N8NWhatsAppService(settings)
            success, n8n_msg_id, error = await n8n_service.send_message(
                phone, rendered_message, message_type=message_type, extra_params=context
            )
            history_data["status"] = "SENT" if success else "FAILED"
            history_data["meta_message_id"] = n8n_msg_id
            history_data["error_message"] = error

        elif settings.mode == "META_CLOUD_API":
            meta_service = MetaWhatsAppService(settings)
            success, meta_msg_id, error = await meta_service.send_message(
                phone, rendered_message
            )
            history_data["status"] = "SENT" if success else "FAILED"
            history_data["meta_message_id"] = meta_msg_id
            history_data["error_message"] = error

        elif settings.mode == "MANUAL_WHATSAPP":
            history_data["status"] = "SENT"

        if settings.save_history:
            record = await self.history_repo.create_entry(history_data)
            await self.commit()
            return record

        return None

    async def send_test_message(
        self,
        recipient_phone: str,
        template_type: str = "ENTRY",
        custom_message: Optional[str] = None,
    ) -> dict:
        """
        Send live test message via backend service using stored settings & credentials.
        """
        settings = await self.get_settings()

        if custom_message and custom_message.strip():
            rendered = custom_message
        else:
            template = await self.template_repo.get_by_type(template_type)
            template_text = template.message if template else f"Test message for {template_type}"
            rendered = self.engine.preview(template_text)

        if settings.mode == "N8N_AUTOMATION":
            n8n_service = N8NWhatsAppService(settings)
            success, meta_msg_id, error_msg = await n8n_service.send_message(
                recipient_phone, rendered, message_type=f"TEST_{template_type}"
            )
            http_status = 200 if success else 400
        else:
            meta_service = MetaWhatsAppService(settings)
            success, meta_msg_id, error_msg, http_status = await meta_service.send_message(
                recipient_phone, rendered
            )

        status_str = "SENT" if success else "FAILED"

        if settings.save_history:
            await self.history_repo.create_entry({
                "visitor_id": None,
                "phone": recipient_phone,
                "message": rendered,
                "message_type": f"TEST_{template_type}",
                "status": status_str,
                "meta_message_id": meta_msg_id,
                "error_message": error_msg,
            })
            await self.commit()

        return {
            "success": success,
            "status": status_str,
            "meta_message_id": meta_msg_id,
            "error_message": error_msg,
            "http_status": http_status,
            "rendered_message": rendered,
        }

    async def send_broadcast_to_recipients(
        self,
        title: str,
        custom_message: str,
        recipients_type: str = "ALL_VISITORS",
        purpose_id: Optional[str] = None,
        created_by: str = "admin",
    ) -> dict:
        """
        Query all registered visitor profiles up to now, filter target phone numbers,
        and dispatch the user-defined broadcast message to every selected visitor.
        """
        from datetime import date, datetime, timezone
        from sqlalchemy.future import select
        from app.models.visitor_profile import VisitorProfile
        from app.models.visit_session import VisitSession

        # 1. Query target visitor profiles
        if recipients_type == "INSIDE":
            stmt = (
                select(VisitorProfile)
                .join(VisitSession, VisitSession.visitor_profile_id == VisitorProfile.id)
                .filter(VisitSession.visit_date == date.today(), VisitSession.status == "INSIDE", VisitorProfile.is_deleted.is_(False))
            )
            res = await self.db.execute(stmt)
            profiles = list(res.scalars().all())
        elif recipients_type == "TODAY":
            stmt = (
                select(VisitorProfile)
                .join(VisitSession, VisitSession.visitor_profile_id == VisitorProfile.id)
                .filter(VisitSession.visit_date == date.today(), VisitorProfile.is_deleted.is_(False))
            )
            res = await self.db.execute(stmt)
            profiles = list(res.scalars().all())
        elif recipients_type == "PURPOSE" and purpose_id:
            stmt = (
                select(VisitorProfile)
                .join(VisitSession, VisitSession.visitor_profile_id == VisitorProfile.id)
                .filter(VisitSession.purpose_id == purpose_id, VisitorProfile.is_deleted.is_(False))
            )
            res = await self.db.execute(stmt)
            profiles = list(res.scalars().all())
        else:
            stmt = select(VisitorProfile).filter(VisitorProfile.is_deleted.is_(False))
            res = await self.db.execute(stmt)
            profiles = list(res.scalars().all())

        # 2. Extract unique non-empty phone numbers
        recipients_map = {}
        for p in profiles:
            if p.phone_number and p.phone_number.strip():
                recipients_map[p.phone_number.strip()] = p

        settings = await self.get_settings()
        n8n_service = N8NWhatsAppService(settings) if settings.mode == "N8N_AUTOMATION" else None
        meta_service = MetaWhatsAppService(settings) if settings.mode == "META_CLOUD_API" else None

        delivered_count = 0
        failed_count = 0

        for phone, prof in recipients_map.items():
            context = {
                "name": prof.name,
                "phone": phone,
                "temple": "Sri Kalki Seva Alayam",
            }
            rendered = self.engine.render(custom_message, context)

            success = True
            msg_id = None
            err = None

            if settings.mode == "N8N_AUTOMATION" and n8n_service:
                success, msg_id, err = await n8n_service.send_message(
                    phone, rendered, message_type="BROADCAST", extra_params=context
                )
            elif settings.mode == "META_CLOUD_API" and meta_service:
                success, msg_id, err = await meta_service.send_message(phone, rendered)

            if success:
                delivered_count += 1
            else:
                failed_count += 1

            if settings.save_history:
                try:
                    await self.history_repo.create_entry({
                        "visitor_id": None,
                        "phone": phone,
                        "message": rendered,
                        "message_type": "BROADCAST",
                        "status": "SENT" if success else "FAILED",
                        "meta_message_id": msg_id,
                        "error_message": err,
                    })
                except Exception:
                    pass

        if settings.save_history:
            await self.commit()

        return {
            "title": title,
            "message": custom_message,
            "recipients_type": recipients_type,
            "recipient_count": len(recipients_map),
            "delivered": delivered_count,
            "failed": failed_count,
            "pending": 0,
            "status": "COMPLETED",
            "created_by": created_by,
            "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        }
