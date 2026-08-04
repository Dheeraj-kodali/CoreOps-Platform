import logging
import httpx
from datetime import datetime, timezone
from typing import Optional, Tuple, Dict, Any
from app.core.config import settings as app_settings
from app.models.communication import CommunicationSetting

logger = logging.getLogger(__name__)


class N8NWhatsAppService:
    """
    Production n8n Business WhatsApp Automation Service.
    Dispatches structured JSON webhooks to n8n workflow triggers for WhatsApp delivery.
    Supports n8n WhatsApp nodes, Evolution API, Baileys, and custom WhatsApp Web integrations.
    """

    def __init__(self, settings: Optional[CommunicationSetting] = None):
        self._webhook_url: str = app_settings.N8N_WHATSAPP_WEBHOOK_URL
        if settings and getattr(settings, 'n8n_webhook_url', None):
            self._webhook_url = settings.n8n_webhook_url
        elif settings and getattr(settings, 'access_token', None) and settings.access_token.startswith("http"):
            self._webhook_url = settings.access_token

        self._api_key: str = app_settings.N8N_API_KEY

    @property
    def is_configured(self) -> bool:
        """Check if a valid n8n webhook URL is configured."""
        return bool(self._webhook_url and self._webhook_url.startswith("http"))

    def build_webhook_payload(
        self,
        recipient_phone: str,
        message_text: str,
        message_type: str = "ENTRY",
        extra_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Construct standard JSON payload for n8n Webhook trigger."""
        clean_phone = recipient_phone.replace(" ", "").replace("-", "")
        if not clean_phone.startswith("+"):
            clean_phone = f"+{clean_phone}"

        return {
            "event": "WHATSAPP_SEND_MESSAGE",
            "recipient_phone": clean_phone,
            "message_text": message_text,
            "message_type": message_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "Sri Kalki Seva Alayam Platform",
            "parameters": extra_params or {},
        }

    async def send_message(
        self,
        recipient_phone: str,
        message_text: str,
        message_type: str = "ENTRY",
        extra_params: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Dispatch WhatsApp automation webhook to n8n.
        Returns: (success: bool, execution_id/msg_id: Optional[str], error: Optional[str])
        """
        if not self.is_configured:
            logger.warning("N8NWhatsAppService: Webhook URL is not configured.")
            return False, None, "n8n Webhook URL is not configured."

        payload = self.build_webhook_payload(recipient_phone, message_text, message_type, extra_params)
        headers = {
            "Content-Type": "application/json",
            "X-N8N-API-KEY": self._api_key,
        }

        try:
            logger.info(f"N8NWhatsAppService: Dispatching webhook to {self._webhook_url} for recipient {recipient_phone}")
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(self._webhook_url, json=payload, headers=headers)
                status_code = response.status_code

                if status_code in (200, 201, 202):
                    res_data = response.json() if response.content else {}
                    execution_id = res_data.get("execution_id") or res_data.get("id") or f"n8n-{int(datetime.now(timezone.utc).timestamp())}"
                    logger.info(f"N8NWhatsAppService: Webhook dispatched successfully. Execution ID: {execution_id}")
                    return True, str(execution_id), None
                else:
                    err_msg = f"HTTP {status_code}: {response.text[:200]}"
                    logger.error(f"N8NWhatsAppService: Delivery failed - {err_msg}")
                    return False, None, err_msg
        except httpx.TimeoutException:
            err_msg = "Connection timeout reaching n8n Webhook Endpoint"
            logger.error(f"N8NWhatsAppService: {err_msg}")
            return False, None, err_msg
        except Exception as e:
            err_msg = f"Exception during n8n webhook dispatch: {str(e)}"
            logger.error(f"N8NWhatsAppService: {err_msg}")
            return False, None, err_msg
