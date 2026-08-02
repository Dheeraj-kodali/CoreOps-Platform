import uuid
from datetime import date, datetime, timezone, time
from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, or_, and_
from sqlalchemy.orm import selectinload

from app.models.visitor_profile import VisitorProfile
from app.models.visit_session import VisitSession
from app.models.visitor import Visitor
from app.repositories.base import BaseRepository


class VisitorRepository(BaseRepository[VisitSession]):

    def __init__(self, session: AsyncSession):
        super().__init__(VisitSession, session)

    # --- VISITOR PROFILE METHODS ---

    async def get_profile_by_phone(self, phone_number: str) -> Optional[VisitorProfile]:
        clean_phone = phone_number.strip()
        stmt = (
            select(VisitorProfile)
            .options(selectinload(VisitorProfile.village), selectinload(VisitorProfile.default_purpose))
            .filter(VisitorProfile.phone_number == clean_phone, VisitorProfile.is_deleted.is_(False))
        )
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def get_profile_by_id(self, profile_id: str) -> Optional[VisitorProfile]:
        stmt = (
            select(VisitorProfile)
            .options(selectinload(VisitorProfile.village), selectinload(VisitorProfile.default_purpose))
            .filter(VisitorProfile.id == profile_id, VisitorProfile.is_deleted.is_(False))
        )
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def create_profile(self, data: dict, user_id: Optional[str] = None) -> VisitorProfile:
        if not data.get("id"):
            data["id"] = str(uuid.uuid4())
        if not data.get("visitor_id"):
            data["visitor_id"] = f"VIP-{str(uuid.uuid4())[:8].upper()}"
        
        profile = VisitorProfile(
            id=data["id"],
            visitor_id=data["visitor_id"],
            name=data["name"].strip(),
            phone_number=data["phone_number"].strip(),
            village_id=data.get("village_id"),
            village_name_custom=data.get("village_name_custom"),
            gender=data.get("gender", "MALE"),
            age=int(data.get("age", 30)),
            default_purpose_id=data.get("default_purpose_id"),
            created_by=user_id,
            updated_by=user_id,
        )
        self.session.add(profile)
        await self.session.flush()
        return profile

    async def update_profile(self, profile: VisitorProfile, data: dict, user_id: Optional[str] = None) -> VisitorProfile:
        for key, val in data.items():
            if hasattr(profile, key) and key not in ("id", "visitor_id", "created_at"):
                setattr(profile, key, val)
        profile.updated_at = datetime.now(timezone.utc)
        if user_id:
            profile.updated_by = user_id
        await self.session.flush()
        return profile

    # --- VISIT SESSION METHODS ---

    async def create_session(self, data: dict, user_id: Optional[str] = None) -> VisitSession:
        session_id = data.get("id") or data.get("visitor_uuid") or str(uuid.uuid4())
        
        visit_date = data.get("visit_date")
        if isinstance(visit_date, str):
            visit_date = datetime.strptime(visit_date[:10], "%Y-%m-%d").date()
        elif not visit_date:
            visit_date = date.today()

        check_in_time = data.get("check_in_time") or data.get("visitor_time")
        if isinstance(check_in_time, str):
            try:
                check_in_time = datetime.strptime(check_in_time, "%H:%M:%S").time()
            except ValueError:
                check_in_time = datetime.now().time()
        elif not check_in_time:
            check_in_time = datetime.now().time()

        session_record = VisitSession(
            id=session_id,
            visitor_profile_id=data["visitor_profile_id"],
            temple_id=data.get("temple_id", "SKSA_MAIN"),
            visit_date=visit_date,
            check_in_time=check_in_time,
            check_out_time=data.get("check_out_time"),
            persons_count=int(data.get("persons_count", 1)),
            purpose_id=data["purpose_id"],
            notes=data.get("notes"),
            volunteer_id=user_id or data.get("volunteer_id", "usr_admin_default"),
            latitude=data.get("latitude"),
            longitude=data.get("longitude"),
            status=data.get("status", "INSIDE"),
            sync_status=data.get("sync_status", "SYNCED"),
            created_by=user_id,
            updated_by=user_id,
        )
        self.session.add(session_record)
        await self.session.flush()
        return session_record

    async def get_session_by_id(self, session_id: str) -> Optional[VisitSession]:
        stmt = (
            select(VisitSession)
            .options(
                selectinload(VisitSession.visitor_profile).selectinload(VisitorProfile.village),
                selectinload(VisitSession.visitor_profile).selectinload(VisitorProfile.default_purpose),
                selectinload(VisitSession.purpose),
                selectinload(VisitSession.volunteer),
            )
            .filter(VisitSession.id == session_id, VisitSession.is_deleted.is_(False))
        )
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def get_sessions_for_profile(self, profile_id: str) -> List[VisitSession]:
        stmt = (
            select(VisitSession)
            .options(selectinload(VisitSession.purpose))
            .filter(VisitSession.visitor_profile_id == profile_id, VisitSession.is_deleted.is_(False))
            .order_by(VisitSession.visit_date.desc(), VisitSession.check_in_time.desc())
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def auto_close_past_sessions(self, current_date: Optional[date] = None) -> List[VisitSession]:
        if current_date is None:
            current_date = date.today()

        stmt = select(VisitSession).filter(
            VisitSession.visit_date < current_date,
            VisitSession.status == "INSIDE",
            VisitSession.is_deleted.is_(False),
        )
        res = await self.session.execute(stmt)
        unfinished = list(res.scalars().all())

        closed_sessions = []
        for s in unfinished:
            s.status = "AUTO_CLOSED"
            s.check_out_time = time(23, 59, 59)
            s.updated_at = datetime.now(timezone.utc)
            if s.notes:
                if "[AUTO_CLOSED]" not in s.notes:
                    s.notes = f"{s.notes} [AUTO_CLOSED]".strip()
            else:
                s.notes = "[AUTO_CLOSED]"
            closed_sessions.append(s)

        if closed_sessions:
            await self.session.flush()

        return closed_sessions

    # --- SEARCH & FILTER FOR VISIT SESSIONS ---

    async def search_and_filter(
        self,
        search: Optional[str] = None,
        purpose_id: Optional[str] = None,
        village_id: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        volunteer_id: Optional[str] = None,
        status_filter: Optional[str] = None,
        page: int = 1,
        limit: int = 20,
    ) -> Tuple[List[VisitSession], int]:
        # Auto-close past sessions before search
        await self.auto_close_past_sessions(date.today())

        stmt = (
            select(VisitSession)
            .join(VisitorProfile, VisitSession.visitor_profile_id == VisitorProfile.id)
            .options(
                selectinload(VisitSession.visitor_profile).selectinload(VisitorProfile.village),
                selectinload(VisitSession.visitor_profile).selectinload(VisitorProfile.default_purpose),
                selectinload(VisitSession.purpose),
                selectinload(VisitSession.volunteer),
            )
        )
        count_stmt = (
            select(func.count(VisitSession.id))
            .join(VisitorProfile, VisitSession.visitor_profile_id == VisitorProfile.id)
        )

        filters = [VisitSession.is_deleted.is_(False)]

        if search:
            pattern = f"%{search}%"
            filters.append(
                or_(
                    VisitorProfile.name.ilike(pattern),
                    VisitorProfile.phone_number.ilike(pattern),
                    VisitorProfile.village_name_custom.ilike(pattern),
                    VisitSession.id.ilike(pattern),
                    VisitorProfile.visitor_id.ilike(pattern),
                )
            )

        if purpose_id:
            filters.append(VisitSession.purpose_id == str(purpose_id))

        if village_id:
            filters.append(VisitorProfile.village_id == str(village_id))

        if date_from:
            filters.append(VisitSession.visit_date >= date_from)

        if date_to:
            filters.append(VisitSession.visit_date <= date_to)

        if volunteer_id:
            filters.append(VisitSession.volunteer_id == str(volunteer_id))

        if status_filter and status_filter.upper() != "ALL":
            sf = status_filter.upper()
            if sf in ("INSIDE", "CHECKED_OUT", "AUTO_CLOSED"):
                filters.append(VisitSession.status == sf)

        stmt = stmt.filter(and_(*filters))
        count_stmt = count_stmt.filter(and_(*filters))

        total = (await self.session.execute(count_stmt)).scalar_one()

        offset = (page - 1) * limit
        stmt = stmt.order_by(VisitSession.visit_date.desc(), VisitSession.created_at.desc()).offset(offset).limit(limit)

        result = await self.session.execute(stmt)
        items = result.scalars().all()

        return list(items), total

    # --- COMPATIBILITY WRAPPERS FOR LEGACY VISITOR QUERIES ---

    async def get_by_id(self, visitor_id: str) -> Optional[VisitSession]:
        return await self.get_session_by_id(visitor_id)

    async def get_by_uuid(self, visitor_uuid: str) -> Optional[VisitSession]:
        return await self.get_session_by_id(visitor_uuid)

    async def check_duplicate(self, name: str, phone_number: str, visitor_date: date) -> Optional[VisitSession]:
        stmt = (
            select(VisitSession)
            .join(VisitorProfile, VisitSession.visitor_profile_id == VisitorProfile.id)
            .filter(
                func.lower(VisitorProfile.name) == name.lower(),
                VisitorProfile.phone_number == phone_number,
                VisitSession.visit_date == visitor_date,
                VisitSession.is_deleted.is_(False),
            )
        )
        res = await self.session.execute(stmt)
        return res.scalars().first()
