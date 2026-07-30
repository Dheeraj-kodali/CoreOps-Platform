from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List, Tuple
from datetime import date

T = TypeVar("T")


class IBaseRepository(ABC, Generic[T]):
    """Abstract interface for standard Data Access Repositories."""

    @abstractmethod
    async def get_by_id(self, entity_id: str) -> Optional[T]:
        pass

    @abstractmethod
    async def get_all(self, limit: int = 100, offset: int = 0) -> List[T]:
        pass

    @abstractmethod
    async def create(self, data: dict, user_id: Optional[str] = None) -> T:
        pass

    @abstractmethod
    async def update(self, entity: T, data: dict, user_id: Optional[str] = None) -> T:
        pass

    @abstractmethod
    async def soft_delete(self, entity_id: str, user_id: Optional[str] = None) -> bool:
        pass


class IVisitorRepository(IBaseRepository[T], ABC):
    """Abstract interface for Visitor Data Operations."""

    @abstractmethod
    async def get_by_uuid(self, visitor_uuid: str) -> Optional[T]:
        pass

    @abstractmethod
    async def check_duplicate(self, name: str, phone_number: str, visitor_date: date) -> Optional[T]:
        pass

    @abstractmethod
    async def search_and_filter(
        self,
        search: Optional[str] = None,
        purpose_id: Optional[str] = None,
        village_id: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        volunteer_id: Optional[str] = None,
        page: int = 1,
        limit: int = 20,
    ) -> Tuple[List[T], int]:
        pass


class IUserRepository(IBaseRepository[T], ABC):
    """Abstract interface for User & Authentication Data Operations."""

    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[T]:
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[T]:
        pass

    @abstractmethod
    async def get_by_id_with_relations(self, user_id: str) -> Optional[T]:
        pass


class ICommunicationRepository(IBaseRepository[T], ABC):
    """Abstract interface for Communication Settings Data Operations."""

    @abstractmethod
    async def get_settings(self) -> Optional[T]:
        pass

    @abstractmethod
    async def get_or_create_settings(self) -> T:
        pass

    @abstractmethod
    async def update_settings(self, data: dict, user_id: Optional[str] = None) -> T:
        pass


class IMessageTemplateRepository(IBaseRepository[T], ABC):
    """Abstract interface for Message Template Data Operations."""

    @abstractmethod
    async def get_by_type(self, template_type: str) -> Optional[T]:
        pass

    @abstractmethod
    async def get_all_templates(self) -> List[T]:
        pass

    @abstractmethod
    async def upsert_template(self, template_type: str, data: dict, user_id: Optional[str] = None) -> T:
        pass


class IMessageHistoryRepository(IBaseRepository[T], ABC):
    """Abstract interface for Communication History Data Operations."""

    @abstractmethod
    async def create_entry(self, data: dict, user_id: Optional[str] = None) -> T:
        pass

    @abstractmethod
    async def get_by_visitor(self, visitor_id: str) -> List[T]:
        pass

    @abstractmethod
    async def get_pending(self) -> List[T]:
        pass

    @abstractmethod
    async def get_failed(self) -> List[T]:
        pass

    @abstractmethod
    async def update_status(self, record_id: str, status: str, meta_message_id: Optional[str] = None, error_message: Optional[str] = None) -> Optional[T]:
        pass
