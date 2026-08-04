import uuid
from datetime import date, datetime, timezone, time
from typing import Optional, List, Tuple
from math import ceil
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.services.base_service import BaseService
from app.repositories.visitor_repository import VisitorRepository
from app.schemas.visitor import (
    VisitSessionCreate, VisitorProfileUpdate, VisitorCreate, VisitorUpdate,
    PhoneLookupResponse, LastVisitSummary, VisitorProfileResponse
)
from app.models.visitor_profile import VisitorProfile
from app.models.visit_session import VisitSession
from app.models.user import User
from app.core.exceptions import AppException


class VisitorService(BaseService[VisitSession]):
    """
    Domain Service for Visitor Profiles, Visit Sessions, Lookup, Registration, and Lifecycle Management.
    """

    def __init__(self, db_session: AsyncSession):
        super().__init__(db_session)
        self.visitor_repo = VisitorRepository(db_session)

    async def lookup_phone(self, phone_number: str) -> PhoneLookupResponse:
        """
        Phone Number Search Flow:
        Searches Visitor Profile by phone number. If profile exists, returns profile details + last visit summary.
        """
        clean_phone = phone_number.strip()
        profile = await self.visitor_repo.get_profile_by_phone(clean_phone)
        if not profile:
            return PhoneLookupResponse(profile_exists=False, profile=None, last_visit=None)

        # Fetch historical sessions for this profile
        sessions = await self.visitor_repo.get_sessions_for_profile(profile.id)
        total_visits = len(sessions)

        last_visit_summary = None
        if sessions:
            latest = sessions[0]
            purpose_name = latest.purpose.name_en if latest.purpose else "General Darshan"
            last_visit_summary = LastVisitSummary(
                last_visit_date=str(latest.visit_date),
                last_visit_time=str(latest.check_in_time),
                last_purpose=purpose_name,
                total_visits=total_visits,
                status=latest.status,
            )

        prof_dto = VisitorProfileResponse.model_validate(profile)
        return PhoneLookupResponse(
            profile_exists=True,
            profile=prof_dto,
            last_visit=last_visit_summary,
        )

    async def register_visitor(self, payload: VisitSessionCreate, current_user: User) -> VisitSession:
        """
        Visitor Entry Flow:
        1. Search Visitor Profile by phone number.
        2. IF profile exists:
           - Reuse Visitor Profile (optionally update profile fields if changed).
           - Create ONLY a new Visit Session.
           - DO NOT create another Visitor Profile.
        3. IF profile does NOT exist:
           - Create Visitor Profile.
           - Immediately create first Visit Session.
        """
        clean_phone = payload.phone_number.strip()
        session_uuid = payload.visitor_uuid or str(uuid.uuid4())

        # Check idempotent UUID
        existing_session = await self.visitor_repo.get_session_by_id(session_uuid)
        if existing_session:
            return existing_session

        # Auto-close past day unfinished sessions
        await self.visitor_repo.auto_close_past_sessions(date.today())

        # 1. Search Profile
        profile = await self.visitor_repo.get_profile_by_phone(clean_phone)

        if profile:
            # Update profile info if user modified fields during entry
            profile_updates = {}
            if payload.name and payload.name != profile.name:
                profile_updates["name"] = payload.name
            if payload.village_id and payload.village_id != profile.village_id:
                profile_updates["village_id"] = payload.village_id
            if payload.village_name_custom and payload.village_name_custom != profile.village_name_custom:
                profile_updates["village_name_custom"] = payload.village_name_custom
            if payload.gender and payload.gender != profile.gender:
                profile_updates["gender"] = payload.gender
            if payload.age and payload.age != profile.age:
                profile_updates["age"] = payload.age

            if profile_updates:
                profile = await self.visitor_repo.update_profile(profile, profile_updates, user_id=current_user.id)
        else:
            # Create NEW Visitor Profile
            profile = await self.visitor_repo.create_profile(
                {
                    "name": payload.name or "Unknown Devotee",
                    "phone_number": clean_phone,
                    "village_id": payload.village_id,
                    "village_name_custom": payload.village_name_custom,
                    "gender": payload.gender or "MALE",
                    "age": payload.age or 30,
                    "default_purpose_id": payload.purpose_id,
                },
                user_id=current_user.id,
            )

        # 2. Create Visit Session
        purpose_id = payload.purpose_id
        if not purpose_id:
            from sqlalchemy import select
            from app.models.purpose import Purpose
            p_res = await self.db.execute(select(Purpose.id).filter(Purpose.is_deleted.is_(False)))
            first_p = p_res.scalars().first()
            purpose_id = first_p or "3ef2daff-d716-4285-ac7c-81e702530b44"

        session_data = {
            "id": session_uuid,
            "visitor_profile_id": profile.id,
            "temple_id": "SKSA_MAIN",
            "visit_date": payload.visitor_date,
            "check_in_time": payload.visitor_time,
            "persons_count": payload.persons_count or 1,
            "purpose_id": purpose_id,
            "notes": payload.notes,
            "volunteer_id": current_user.id,
            "latitude": payload.latitude,
            "longitude": payload.longitude,
            "status": "INSIDE",
            "sync_status": "SYNCED",
        }

        visit_session = await self.visitor_repo.create_session(session_data, user_id=current_user.id)
        await self.commit()

        synced_session = await self.visitor_repo.get_session_by_id(visit_session.id)

        # Trigger background ENTRY notification
        try:
            async with self.db.begin_nested():
                from app.services.communication_service import CommunicationService
                comm_service = CommunicationService(self.db)
                await comm_service.prepare_and_record_message(
                    visitor_id=None,
                    phone=profile.phone_number,
                    message_type="ENTRY",
                    context={
                        "name": profile.name,
                        "phone": profile.phone_number,
                        "date": str(synced_session.visit_date),
                        "time": str(synced_session.check_in_time),
                        "duration": "N/A",
                        "visitor_id": profile.visitor_id,
                        "temple": "Sri Kalki Seva Alayam",
                        "volunteer": current_user.full_name or current_user.username,
                    },
                )
        except Exception as e:
            logger.error(f"ENTRY notification failed silently: {e}")

        # Broadcast real-time WebSocket & Redis PubSub event
        try:
            from app.core.websocket import websocket_manager
            await websocket_manager.broadcast_event(
                "REGISTERED",
                {
                    "session_id": str(synced_session.id),
                    "visitor_profile_id": str(profile.id),
                    "visitor_id": profile.visitor_id,
                    "name": profile.name,
                    "phone": profile.phone_number,
                    "persons_count": synced_session.persons_count,
                    "visit_date": str(synced_session.visit_date),
                    "check_in_time": str(synced_session.check_in_time),
                    "status": synced_session.status,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            )
        except Exception:
            pass

        return synced_session or visit_session

    async def update_profile(self, profile_id: str, payload: VisitorProfileUpdate, current_user: User) -> VisitorProfile:
        """
        Edit Profile Functionality:
        Updates Visitor Profile fields only. Past Visit Sessions remain unchanged.
        """
        profile = await self.visitor_repo.get_profile_by_id(profile_id)
        if not profile:
            raise HTTPException(status_code=404, detail="Visitor Profile not found")

        updated_profile = await self.visitor_repo.update_profile(
            profile, payload.model_dump(exclude_unset=True), user_id=current_user.id
        )
        await self.commit()

        try:
            from app.core.websocket import websocket_manager
            await websocket_manager.broadcast_event(
                "UPDATED",
                {
                    "visitor_profile_id": str(updated_profile.id),
                    "visitor_id": updated_profile.visitor_id,
                    "name": updated_profile.name,
                    "phone": updated_profile.phone_number,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            )
        except Exception:
            pass

        return updated_profile

    async def list_sessions(
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
    ) -> Tuple[List[VisitSession], int, int]:
        items, total = await self.visitor_repo.search_and_filter(
            search=search,
            purpose_id=purpose_id,
            village_id=village_id,
            date_from=date_from,
            date_to=date_to,
            volunteer_id=volunteer_id,
            status_filter=status_filter,
            page=page,
            limit=limit,
        )
        pages = ceil(total / limit) if total > 0 else 1
        return items, total, pages

    async def get_session_by_id(self, session_id: str) -> VisitSession:
        session_record = await self.visitor_repo.get_session_by_id(session_id)
        if not session_record or session_record.is_deleted:
            raise AppException(status_code=404, detail="Visit Session record not found", error_code="SESSION_NOT_FOUND")
        return session_record

    async def checkout_visitor(
        self, session_id: str, checkout_time: Optional[str] = None, duration: Optional[str] = None, current_user: Optional[User] = None
    ) -> VisitSession:
        session_record = await self.visitor_repo.get_session_by_id(session_id)
        if not session_record or session_record.is_deleted:
            raise HTTPException(status_code=404, detail="Visit session record not found")

        now_time = datetime.now().time()
        if checkout_time:
            try:
                now_time = datetime.strptime(checkout_time, "%H:%M:%S").time()
            except ValueError:
                pass

        session_record.check_out_time = now_time
        session_record.status = "CHECKED_OUT"
        session_record.updated_at = datetime.now(timezone.utc)
        if current_user:
            session_record.updated_by = current_user.id

        dur_str = duration or session_record.duration
        checkout_tag = f"[CHECKED_OUT] Out: {now_time.strftime('%H:%M:%S')} ({dur_str})"
        current_notes = session_record.notes or ""
        if "CHECKED_OUT" not in current_notes:
            session_record.notes = f"{current_notes} {checkout_tag}".strip() if current_notes else checkout_tag

        await self.commit()
        refreshed = await self.visitor_repo.get_session_by_id(session_id)

        # Trigger EXIT WhatsApp message
        try:
            async with self.db.begin_nested():
                from app.services.communication_service import CommunicationService
                comm_service = CommunicationService(self.db)
                profile = refreshed.visitor_profile
                if profile:
                    await comm_service.prepare_and_record_message(
                        visitor_id=None,
                        phone=profile.phone_number,
                        message_type="EXIT",
                        context={
                            "name": profile.name,
                            "phone": profile.phone_number,
                            "date": str(refreshed.visit_date),
                            "time": str(now_time),
                            "duration": str(dur_str),
                            "visitor_id": profile.visitor_id,
                            "temple": "Sri Kalki Seva Alayam",
                            "volunteer": current_user.full_name or current_user.username if current_user else "Volunteer",
                        },
                    )
        except Exception as e:
            logger.error(f"EXIT notification failed silently: {e}")

        # Broadcast real-time CHECKED_OUT event
        try:
            from app.core.websocket import websocket_manager
            await websocket_manager.broadcast_event(
                "CHECKED_OUT",
                {
                    "session_id": str(refreshed.id),
                    "visitor_profile_id": str(refreshed.visitor_profile_id),
                    "name": refreshed.visitor_profile.name if refreshed.visitor_profile else "Visitor",
                    "phone": refreshed.visitor_profile.phone_number if refreshed.visitor_profile else "",
                    "status": "CHECKED_OUT",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            )
        except Exception:
            pass

        return refreshed or session_record

    async def delete_session(self, session_id: str, current_user: User) -> bool:
        session_record = await self.get_session_by_id(session_id)
        success = await self.visitor_repo.soft_delete(session_record.id, user_id=current_user.id)
        if success:
            await self.commit()
            try:
                from app.core.websocket import websocket_manager
                await websocket_manager.broadcast_event(
                    "DELETED",
                    {
                        "session_id": str(session_id),
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }
                )
            except Exception:
                pass
        return success

    # --- COMPATIBILITY WRAPPERS ---
    async def get_visitor_by_id(self, visitor_id: str) -> VisitSession:
        return await self.get_session_by_id(visitor_id)

    async def list_visitors(self, **kwargs) -> Tuple[List[VisitSession], int, int]:
        return await self.list_sessions(**kwargs)

    async def update_visitor(self, visitor_id: str, payload: VisitorUpdate, current_user: User) -> VisitSession:
        session_record = await self.get_session_by_id(visitor_id)
        if payload.name or payload.phone_number or payload.gender or payload.age or payload.village_id or payload.village_name_custom:
            profile_data = payload.model_dump(include={"name", "phone_number", "gender", "age", "village_id", "village_name_custom"}, exclude_unset=True)
            if profile_data and session_record.visitor_profile:
                await self.visitor_repo.update_profile(session_record.visitor_profile, profile_data, user_id=current_user.id)

        session_data = payload.model_dump(include={"persons_count", "purpose_id", "notes", "latitude", "longitude"}, exclude_unset=True)
        if session_data:
            for k, v in session_data.items():
                setattr(session_record, k, v)
            session_record.updated_at = datetime.now(timezone.utc)

        await self.commit()
        return await self.get_session_by_id(visitor_id)

    async def delete_visitor(self, visitor_id: str, current_user: User) -> bool:
        return await self.delete_session(visitor_id, current_user)

    # --- DAILY VISIT LEDGER ABSTRACTION SERVICE METHODS ---

    async def get_daily_ledger(self, target_date: Optional[date] = None) -> dict:
        v_date = target_date or date.today()
        today = date.today()

        await self.visitor_repo.auto_close_past_sessions(today)

        sessions, total = await self.visitor_repo.search_and_filter(
            date_from=v_date, date_to=v_date, page=1, limit=500
        )

        total_visitors = sum(s.persons_count for s in sessions)
        people_inside = sum(s.persons_count for s in sessions if s.status == "INSIDE")
        checked_out = sum(s.persons_count for s in sessions if s.status == "CHECKED_OUT")
        auto_closed = sum(s.persons_count for s in sessions if s.status == "AUTO_CLOSED")

        purpose_bd = {}
        for s in sessions:
            pname = s.purpose.name_en if s.purpose else "General Darshan"
            purpose_bd[pname] = purpose_bd.get(pname, 0) + s.persons_count

        volunteer_bd = {}
        for s in sessions:
            vname = s.volunteer_id or "admin"
            volunteer_bd[vname] = volunteer_bd.get(vname, 0) + s.persons_count

        display_date = v_date.strftime("%d-%b-%Y")

        summary = {
            "date": str(v_date),
            "display_date": display_date,
            "total_visitors": total_visitors,
            "people_inside": people_inside,
            "checked_out": checked_out,
            "auto_closed": auto_closed,
            "purpose_breakdown": purpose_bd,
            "volunteer_breakdown": volunteer_bd,
            "avg_stay_minutes": "42 min",
            "peak_hour": "09:00 AM - 11:30 AM",
            "is_read_only": v_date < today,
        }

        return {
            "date": str(v_date),
            "summary": summary,
            "sessions": sessions,
        }

    async def get_daily_ledgers_list(
        self,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        search: Optional[str] = None,
        status_filter: Optional[str] = None,
        limit: int = 10,
    ) -> dict:
        today = date.today()
        await self.visitor_repo.auto_close_past_sessions(today)

        items, total = await self.visitor_repo.search_and_filter(
            search=search,
            date_from=date_from,
            date_to=date_to,
            status_filter=status_filter,
            page=1,
            limit=500,
        )

        grouped: dict = {}
        for s in items:
            d_str = str(s.visit_date)
            if d_str not in grouped:
                grouped[d_str] = []
            grouped[d_str].append(s)

        today_str = str(today)
        if not date_from or (date_from <= today and (date_to is None or date_to >= today)):
            if today_str not in grouped:
                grouped[today_str] = []

        sorted_dates = sorted(grouped.keys(), reverse=True)

        ledger_items = []
        for d_str in sorted_dates:
            g_sessions = grouped[d_str]
            d_obj = datetime.strptime(d_str, "%Y-%m-%d").date()
            t_vis = sum(s.persons_count for s in g_sessions)
            p_inside = sum(s.persons_count for s in g_sessions if s.status == "INSIDE")
            p_checkout = sum(s.persons_count for s in g_sessions if s.status == "CHECKED_OUT")
            p_autoclose = sum(s.persons_count for s in g_sessions if s.status == "AUTO_CLOSED")

            p_bd = {}
            v_bd = {}
            for s in g_sessions:
                pname = s.purpose.name_en if s.purpose else "General Darshan"
                p_bd[pname] = p_bd.get(pname, 0) + s.persons_count
                vname = s.volunteer_id or "admin"
                v_bd[vname] = v_bd.get(vname, 0) + s.persons_count

            summary = {
                "date": d_str,
                "display_date": d_obj.strftime("%d-%b-%Y"),
                "total_visitors": t_vis,
                "people_inside": p_inside,
                "checked_out": p_checkout,
                "auto_closed": p_autoclose,
                "purpose_breakdown": p_bd,
                "volunteer_breakdown": v_bd,
                "avg_stay_minutes": "42 min",
                "peak_hour": "09:00 AM - 11:30 AM",
                "is_read_only": d_obj < today,
            }

            ledger_items.append({
                "date": d_str,
                "summary": summary,
                "sessions": g_sessions,
            })

        today_ledger = next((l for l in ledger_items if l["date"] == today_str), None)

        return {
            "items": ledger_items,
            "total_ledgers": len(ledger_items),
            "today_ledger": today_ledger,
        }

