from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from app.models.communication import CommunicationHistoryRecord
from app.repositories.base import BaseRepository


class MessageHistoryRepository(BaseRepository[CommunicationHistoryRecord]):

    def __init__(self, session: AsyncSession):
        super().__init__(CommunicationHistoryRecord, session)

    async def create_entry(
        self, data: dict, user_id: Optional[str] = None
    ) -> CommunicationHistoryRecord:
        """Insert a new communication history record."""
        return await self.create(data, user_id=user_id)

    async def get_by_visitor(
        self, visitor_id: str
    ) -> List[CommunicationHistoryRecord]:
        """Fetch all communication history records for a specific visitor."""
        stmt = (
            select(CommunicationHistoryRecord)
            .filter(
                CommunicationHistoryRecord.visitor_id == visitor_id,
                CommunicationHistoryRecord.is_deleted.is_(False),
            )
            .order_by(CommunicationHistoryRecord.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_paginated(
        self, page: int = 1, limit: int = 20
    ) -> Tuple[List[CommunicationHistoryRecord], int]:
        """Fetch paginated communication history records."""
        count_stmt = select(func.count(CommunicationHistoryRecord.id)).filter(
            CommunicationHistoryRecord.is_deleted.is_(False)
        )
        count_result = await self.session.execute(count_stmt)
        total = count_result.scalar_one()

        offset = (page - 1) * limit
        stmt = (
            select(CommunicationHistoryRecord)
            .filter(CommunicationHistoryRecord.is_deleted.is_(False))
            .order_by(CommunicationHistoryRecord.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        items = list(result.scalars().all())

        return items, total

    async def get_pending(self) -> List[CommunicationHistoryRecord]:
        """Fetch all records with PENDING status for processing."""
        stmt = (
            select(CommunicationHistoryRecord)
            .filter(
                CommunicationHistoryRecord.status == "PENDING",
                CommunicationHistoryRecord.is_deleted.is_(False),
            )
            .order_by(CommunicationHistoryRecord.created_at.asc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_failed(self) -> List[CommunicationHistoryRecord]:
        """Fetch all records with FAILED status for retry."""
        stmt = (
            select(CommunicationHistoryRecord)
            .filter(
                CommunicationHistoryRecord.status == "FAILED",
                CommunicationHistoryRecord.is_deleted.is_(False),
            )
            .order_by(CommunicationHistoryRecord.created_at.asc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update_status(
        self,
        record_id: str,
        status: str,
        meta_message_id: Optional[str] = None,
        error_message: Optional[str] = None,
    ) -> Optional[CommunicationHistoryRecord]:
        """Update the status of a history record after a send attempt."""
        record = await self.get_by_id(record_id)
        if not record:
            return None

        update_data = {"status": status}
        if meta_message_id is not None:
            update_data["meta_message_id"] = meta_message_id
        if error_message is not None:
            update_data["error_message"] = error_message

        return await self.update(record, update_data)
