import logging
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal
from app.core.events import event_bus, BaseDomainEvent
from app.repositories.visitor_repository import VisitorRepository
from app.repositories.user_repository import UserRepository, SessionRepository

logger = logging.getLogger(__name__)


class UnitOfWork:
    """
    Enterprise Unit of Work (UoW) Pattern.
    Coordinates database session context, repository lifecycle, atomic commit/rollback,
    and automatic Domain Event dispatch upon transaction success.
    """

    def __init__(self, session_factory=AsyncSessionLocal):
        self.session_factory = session_factory
        self.db: Optional[AsyncSession] = None
        self._pending_events: List[BaseDomainEvent] = []

    async def __aenter__(self):
        self.db = self.session_factory()
        self.visitors = VisitorRepository(self.db)
        self.users = UserRepository(self.db)
        self.sessions = SessionRepository(self.db)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            await self.rollback()
        if self.db:
            await self.db.close()

    def collect_event(self, event: BaseDomainEvent):
        """Queue a domain event to be dispatched upon successful transaction commit."""
        self._pending_events.append(event)

    async def commit(self):
        """Commit atomic transaction and dispatch all collected domain events."""
        if not self.db:
            return
        try:
            await self.db.commit()
            logger.debug("[UnitOfWork] Database transaction committed successfully")

            # Dispatch queued domain events
            while self._pending_events:
                event = self._pending_events.pop(0)
                await event_bus.publish(event)
        except Exception as e:
            await self.db.rollback()
            logger.error(f"[UnitOfWork Commit Failure] Rolling back transaction: {str(e)}")
            raise e

    async def rollback(self):
        """Rollback active transaction."""
        if self.db:
            await self.db.rollback()
            self._pending_events.clear()
            logger.debug("[UnitOfWork] Database transaction rolled back")
