import logging
from typing import Generic, TypeVar
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import AppException

logger = logging.getLogger(__name__)
T = TypeVar("T")


class BaseService(Generic[T]):
    """
    Base Enterprise Domain Service providing Unit-of-Work (UoW) transaction context management
    and standardized error handling boundaries.
    """

    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def commit(self):
        """Commit current transaction context."""
        try:
            await self.db.commit()
        except Exception as e:
            await self.db.rollback()
            logger.error(f"[Unit-of-Work Commit Error]: {str(e)}")
            raise AppException(status_code=500, detail="Database transaction commit failed", error_code="UOW_COMMIT_ERROR")

    async def rollback(self):
        """Rollback current transaction context."""
        await self.db.rollback()
