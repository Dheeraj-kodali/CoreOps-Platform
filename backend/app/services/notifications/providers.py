import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class NotificationPayload:
    """Standardized Notification Data Container."""

    def __init__(self, recipient: str, title: str, body: str, template_name: str = None, metadata: dict = None):
        self.recipient = recipient
        self.title = title
        self.body = body
        self.template_name = template_name
        self.metadata = metadata or {}


class BaseNotificationProvider(ABC):
    """Abstract Strategy Provider for Notification Drivers."""

    @property
    @abstractmethod
    def channel_name(self) -> str:
        pass

    @abstractmethod
    async def send(self, payload: NotificationPayload) -> bool:
        pass


class SMSNotificationProvider(BaseNotificationProvider):
    """SMS Channel Driver (DLT Compliant SMS Gateway)."""

    @property
    def channel_name(self) -> str:
        return "SMS"

    async def send(self, payload: NotificationPayload) -> bool:
        logger.info(f"[SMS Provider Driver] Dispatching SMS to {payload.recipient}: {payload.body}")
        # Call DLT SMS Gateway REST API
        return True


class WhatsAppNotificationProvider(BaseNotificationProvider):
    """WhatsApp Business Cloud API Driver."""

    @property
    def channel_name(self) -> str:
        return "WHATSAPP"

    async def send(self, payload: NotificationPayload) -> bool:
        logger.info(f"[WhatsApp Provider Driver] Dispatching WhatsApp Template '{payload.template_name}' to {payload.recipient}")
        # Call Meta Cloud API Graph Endpoint
        return True


class EmailNotificationProvider(BaseNotificationProvider):
    """Email Gateway Driver (SMTP / SendGrid)."""

    @property
    def channel_name(self) -> str:
        return "EMAIL"

    async def send(self, payload: NotificationPayload) -> bool:
        logger.info(f"[Email Provider Driver] Dispatching Email '{payload.title}' to {payload.recipient}")
        # Call SMTP / SendGrid API
        return True


class PushNotificationProvider(BaseNotificationProvider):
    """Firebase Cloud Messaging (FCM) Push Driver."""

    @property
    def channel_name(self) -> str:
        return "PUSH"

    async def send(self, payload: NotificationPayload) -> bool:
        logger.info(f"[Push Provider Driver] Dispatching FCM Push Notification to device token {payload.recipient}")
        # Call Firebase Cloud Messaging SDK
        return True
