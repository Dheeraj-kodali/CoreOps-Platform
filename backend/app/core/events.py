import logging
import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Type, Callable, Awaitable

logger = logging.getLogger(__name__)


class BaseDomainEvent:
    """Base class for all enterprise Domain Events."""

    def __init__(self, event_type: str, tenant_id: str = None):
        self.event_id = str(id(self))
        self.event_type = event_type
        self.tenant_id = tenant_id
        self.occurred_at = datetime.now(timezone.utc)


class VisitorRegisteredEvent(BaseDomainEvent):
    """Fired when a visitor is successfully registered."""

    def __init__(self, visitor_id: str, visitor_uuid: str, phone_number: str, name: str, temple_id: str = None):
        super().__init__("VISITOR_REGISTERED", tenant_id=temple_id)
        self.visitor_id = visitor_id
        self.visitor_uuid = visitor_uuid
        self.phone_number = phone_number
        self.name = name


class UserLoggedInEvent(BaseDomainEvent):
    """Fired when a user successfully authenticates."""

    def __init__(self, user_id: str, username: str, ip_address: str = None):
        super().__init__("USER_LOGGED_IN")
        self.user_id = user_id
        self.username = username
        self.ip_address = ip_address


class SyncBatchProcessedEvent(BaseDomainEvent):
    """Fired when an offline batch sync transaction completes."""

    def __init__(self, processed_count: int, success_count: int, failure_count: int, client_id: str):
        super().__init__("SYNC_BATCH_PROCESSED")
        self.processed_count = processed_count
        self.success_count = success_count
        self.failure_count = failure_count
        self.client_id = client_id


EventHandler = Callable[[BaseDomainEvent], Awaitable[None]]


class EventBus:
    """
    Decoupled Asynchronous Domain Event Bus.
    Allows services to publish domain events without direct coupling to listeners or side-effects.
    """

    def __init__(self):
        self._subscribers: Dict[Type[BaseDomainEvent], List[EventHandler]] = {}

    def subscribe(self, event_type: Type[BaseDomainEvent], handler: EventHandler):
        """Register an async handler function for a specific domain event type."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)
        logger.info(f"[EventBus] Subscribed handler '{handler.__name__}' to '{event_type.__name__}'")

    async def publish(self, event: BaseDomainEvent):
        """Publish a domain event to all registered async subscriber handlers."""
        event_type = type(event)
        handlers = self._subscribers.get(event_type, [])
        logger.info(f"[EventBus] Publishing event '{event.event_type}' (Handlers registered: {len(handlers)})")

        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception as e:
                logger.error(f"[EventBus Handler Error] Failed executing '{handler.__name__}' for event '{event.event_type}': {str(e)}")


# Global Singleton Event Bus instance
event_bus = EventBus()
