from abc import ABC, abstractmethod
from typing import Optional, List, Tuple, Any
from datetime import date


class IVisitorService(ABC):
    """Abstract Domain Interface for Visitor Management Operations."""

    @abstractmethod
    async def register_visitor(self, payload: Any, current_user: Any) -> Any:
        pass

    @abstractmethod
    async def list_visitors(
        self,
        search: Optional[str] = None,
        purpose_id: Optional[str] = None,
        village_id: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        volunteer_id: Optional[str] = None,
        page: int = 1,
        limit: int = 20,
    ) -> Tuple[List[Any], int, int]:
        pass

    @abstractmethod
    async def check_duplicate(self, name: str, phone_number: str, visitor_date: date) -> Optional[Any]:
        pass


class ISyncService(ABC):
    """Abstract Domain Interface for Offline Batch Sync Operations."""

    @abstractmethod
    async def process_batch_sync(self, request: Any, current_user: Any) -> Any:
        pass


class INotificationService(ABC):
    """Abstract Notification Orchestrator Interface supporting SMS, WhatsApp, Email, and Push Notifications."""

    @abstractmethod
    async def dispatch_notification(
        self,
        channel: str,
        recipient: str,
        template_name: str,
        context: dict,
        temple_id: Optional[str] = None
    ) -> bool:
        pass


class ICommunicationService(ABC):
    """Abstract Domain Interface for Communication Settings and WhatsApp Message Management."""

    @abstractmethod
    async def get_settings(self) -> Any:
        pass

    @abstractmethod
    async def update_settings(self, payload: Any, current_user: Any) -> Any:
        pass

    @abstractmethod
    async def get_templates(self) -> List[Any]:
        pass

    @abstractmethod
    async def update_template(self, template_type: str, payload: Any, current_user: Any) -> Any:
        pass

    @abstractmethod
    async def preview_message(self, template_type: str, custom_message: Optional[str] = None) -> dict:
        pass

    @abstractmethod
    async def get_history_for_visitor(self, visitor_id: str) -> List[Any]:
        pass

    @abstractmethod
    async def get_all_history(self, page: int = 1, limit: int = 20) -> Tuple[List[Any], int, int]:
        pass
