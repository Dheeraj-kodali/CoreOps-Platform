import logging
from app.core.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=5)
def send_sms_notification_task(self, phone_number: str, message: str, temple_id: str = None):
    """
    Celery background task to dispatch SMS notification.
    """
    try:
        logger.info(f"[Celery Task] Dispatching SMS to {phone_number} (Temple: {temple_id})")
        # Provider HTTP Integration Call (Placeholder for live DLT SMS gateway)
        provider_response = {"status": "SUCCESS", "message_id": f"sms_msg_{self.request.id}"}
        return provider_response
    except Exception as exc:
        logger.error(f"[Celery Task Failure] SMS delivery failed to {phone_number}: {str(exc)}")
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=5)
def send_whatsapp_notification_task(self, phone_number: str, template_name: str, parameters: dict, temple_id: str = None):
    """
    Celery background task to dispatch WhatsApp template notification via Meta Cloud API.
    """
    try:
        logger.info(f"[Celery Task] Dispatching WhatsApp template '{template_name}' to {phone_number}")
        # Meta Cloud API Integration Call (Placeholder)
        provider_response = {"status": "DELIVERED", "wamid": f"wamid_{self.request.id}"}
        return provider_response
    except Exception as exc:
        logger.error(f"[Celery Task Failure] WhatsApp delivery failed to {phone_number}: {str(exc)}")
        raise self.retry(exc=exc)
