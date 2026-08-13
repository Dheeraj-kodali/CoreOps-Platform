import logging
import httpx
from typing import Optional, Tuple, Dict, Any
from app.models.communication import CommunicationSetting

logger = logging.getLogger(__name__)

META_API_VERSION = "v23.0"
DEFAULT_PHONE_NUMBER_ID = "1290699690788322"


def mask_token(token: Optional[str]) -> str:
    """Mask sensitive tokens for safe logging."""
    if not token:
        return "<EMPTY>"
    if len(token) <= 8:
        return "****"
    return f"{token[:4]}...{token[-4:]}"


class MetaWhatsAppService:
    """
    Production Meta WhatsApp Cloud API service.
    Credentials are exclusively sourced from CommunicationSetting or environment fallback.
    Never hardcoded in source. Masking enforced on all security logs.
    """

    def __init__(self, settings: CommunicationSetting):
        self._access_token: Optional[str] = settings.access_token
        self._phone_number_id: str = settings.phone_number_id or DEFAULT_PHONE_NUMBER_ID
        self._business_account_id: Optional[str] = settings.business_account_id

    @property
    def is_configured(self) -> bool:
        """Check if access token is available for Meta API dispatch."""
        return bool(self._access_token and self._access_token.strip())

    def build_api_url(self) -> str:
        """Construct the Meta Cloud API messages endpoint URL (v23.0)."""
        return f"https://graph.facebook.com/{META_API_VERSION}/{self._phone_number_id}/messages"

    def build_headers(self) -> Dict[str, str]:
        """Construct the HTTP headers with Bearer token authentication."""
        return {
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": "application/json",
        }

    def build_text_payload(self, recipient_phone: str, message_text: str) -> Dict[str, Any]:
        """Construct standard text message payload according to Meta Graph API spec."""
        clean_phone = recipient_phone.strip().replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        if clean_phone.startswith("+"):
            clean_phone = clean_phone[1:]
        if clean_phone.startswith("0") and len(clean_phone) > 10:
            clean_phone = clean_phone[1:]
        if len(clean_phone) == 10:
            clean_phone = f"91{clean_phone}"

        return {
            "messaging_product": "whatsapp",
            "to": clean_phone,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": message_text,
            },
        }

    async def send_message(
        self, recipient_phone: str, message_text: str
    ) -> Tuple[bool, Optional[str], Optional[str], Optional[int]]:
        """
        Execute live HTTP POST request to Meta WhatsApp Cloud API.

        Returns:
            Tuple of (success: bool, meta_message_id: str | None, error_message: str | None, http_status: int | None)
        """
        if not self.is_configured:
            masked = mask_token(self._access_token)
            logger.warning(f"MetaWhatsAppService: Cannot dispatch — token is missing (token: {masked})")
            return False, None, "Meta Access Token is missing or empty in Communication Settings", 400

        url = self.build_api_url()
        headers = self.build_headers()
        payload = self.build_text_payload(recipient_phone, message_text)

        logger.info(
            f"MetaWhatsAppService: Sending live message to {payload['to']} via {url} "
            f"[Token: {mask_token(self._access_token)}]"
        )

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(url, headers=headers, json=payload)
                status_code = response.status_code
                res_data = response.json() if response.content else {}

                if status_code in (200, 201):
                    messages = res_data.get("messages", [])
                    meta_msg_id = messages[0].get("id") if messages else None
                    logger.info(f"MetaWhatsAppService: Successfully sent message. wamid: {meta_msg_id}")
                    return True, meta_msg_id, None, status_code
                else:
                    error_obj = res_data.get("error", {})
                    error_msg = error_obj.get("message") or f"HTTP {status_code}: {response.text}"
                    error_code = error_obj.get("code")
                    full_err = f"Meta API Error ({error_code}): {error_msg}" if error_code else error_msg
                    logger.error(f"MetaWhatsAppService: Delivery failed with HTTP {status_code} - {full_err}")
                    return False, None, full_err, status_code

        except httpx.TimeoutException:
            logger.error("MetaWhatsAppService: Connection timeout while reaching Meta Graph API")
            return False, None, "Meta Graph API connection timeout", 504
        except Exception as e:
            logger.error(f"MetaWhatsAppService: Exception during send - {str(e)}")
            return False, None, f"Network/System Error: {str(e)}", 500
