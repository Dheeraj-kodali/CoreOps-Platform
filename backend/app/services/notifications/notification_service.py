import logging
from typing import Dict, Optional
from app.interfaces.services import INotificationService
from app.services.notifications.providers import (
    BaseNotificationProvider,
    SMSNotificationProvider,
    WhatsAppNotificationProvider,
    EmailNotificationProvider,
    PushNotificationProvider,
    NotificationPayload,
)
from app.tasks.notifications import send_sms_notification_task, send_whatsapp_notification_task

logger = logging.getLogger(__name__)


class UnifiedNotificationService(INotificationService):
    """
    Enterprise Unified Notification Orchestrator.
    Supports SMS, WhatsApp, Email, and Push notifications transparently without modifying business logic.
    """

    def __init__(self):
        self._providers: Dict[str, BaseNotificationProvider] = {
            "SMS": SMSNotificationProvider(),
            "WHATSAPP": WhatsAppNotificationProvider(),
            "EMAIL": EmailNotificationProvider(),
            "PUSH": PushNotificationProvider(),
        }

    def register_provider(self, provider: BaseNotificationProvider):
        """Register or override a notification provider driver."""
        self._providers[provider.channel_name.upper()] = provider
        logger.info(f"[UnifiedNotificationService] Registered provider driver for channel '{provider.channel_name}'")

    async def dispatch_notification(
        self,
        channel: str,
        recipient: str,
        template_name: str,
        context: dict,
        temple_id: Optional[str] = None
    ) -> bool:
        channel_key = channel.upper()
        if channel_key not in self._providers:
            logger.error(f"[Notification Service Error] Unsupported channel '{channel}'")
            return False

        logger.info(f"[Notification Service] Queuing '{channel_key}' notification for '{recipient}' via Celery worker")

        # Async background worker queue dispatch
        if channel_key == "SMS":
            body_text = f"Darshan Token: {context.get('visitor_uuid', '')}. Thank you for visiting."
            send_sms_notification_task.delay(phone_number=recipient, message=body_text, temple_id=temple_id)
        elif channel_key == "WHATSAPP":
            send_whatsapp_notification_task.delay(phone_number=recipient, template_name=template_name, parameters=context, temple_id=temple_id)
        else:
            # Direct provider fallback for EMAIL / PUSH
            provider = self._providers[channel_key]
            payload = NotificationPayload(
                recipient=recipient,
                title=context.get("title", "Temple Notification"),
                body=context.get("body", ""),
                template_name=template_name,
                metadata=context
            )
            await provider.send(payload)

        return True


# Global Singleton Notification Service instance
notification_service = UnifiedNotificationService()
