from datetime import date
from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, or_, and_
from sqlalchemy.orm import selectinload
from app.models.visitor import Visitor
from app.repositories.base import BaseRepository


class VisitorRepository(BaseRepository[Visitor]):

    def __init__(self, session: AsyncSession):
        super().__init__(Visitor, session)

    async def get_by_id(self, visitor_id: str) -> Optional[Visitor]:
        stmt = (
            select(Visitor)
            .options(selectinload(Visitor.purpose), selectinload(Visitor.village))
            .filter(Visitor.id == visitor_id, Visitor.is_deleted.is_(False))
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_by_uuid(self, visitor_uuid: str) -> Optional[Visitor]:
        stmt = (
            select(Visitor)
            .options(selectinload(Visitor.purpose), selectinload(Visitor.village))
            .filter(Visitor.visitor_uuid == visitor_uuid, Visitor.is_deleted.is_(False))
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def check_duplicate(self, name: str, phone_number: str, visitor_date: date) -> Optional[Visitor]:
        stmt = select(Visitor).filter(
            func.lower(Visitor.name) == name.lower(),
            Visitor.phone_number == phone_number,
            Visitor.visitor_date == visitor_date,
            Visitor.is_deleted.is_(False),
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

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
    ) -> Tuple[List[Visitor], int]:
        stmt = select(Visitor).options(selectinload(Visitor.purpose), selectinload(Visitor.village))
        count_stmt = select(func.count(Visitor.id))

        filters = [Visitor.is_deleted.is_(False)]
        if search:
            search_pattern = f"%{search}%"
            filters.append(
                or_(
                    Visitor.name.ilike(search_pattern),
                    Visitor.phone_number.ilike(search_pattern),
                    Visitor.village_name_custom.ilike(search_pattern),
                    Visitor.temple_service.ilike(search_pattern),
                )
            )
        if purpose_id:
            filters.append(Visitor.purpose_id == str(purpose_id))
        if village_id:
            filters.append(Visitor.village_id == str(village_id))
        if date_from:
            filters.append(Visitor.visitor_date >= date_from)
        if date_to:
            filters.append(Visitor.visitor_date <= date_to)
        if volunteer_id:
            filters.append(Visitor.volunteer_id == str(volunteer_id))

        stmt = stmt.filter(and_(*filters))
        count_stmt = count_stmt.filter(and_(*filters))

        total_result = await self.session.execute(count_stmt)
        total = total_result.scalar_one()

        offset = (page - 1) * limit
        stmt = stmt.order_by(Visitor.created_at.desc()).offset(offset).limit(limit)

        result = await self.session.execute(stmt)
        items = result.scalars().all()

        return list(items), total
