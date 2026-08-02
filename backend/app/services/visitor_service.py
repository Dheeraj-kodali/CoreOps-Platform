from datetime import date
from typing import Optional, List, Tuple
from math import ceil
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.base_service import BaseService
from app.repositories.visitor_repository import VisitorRepository
from app.schemas.visitor import VisitorCreate, VisitorUpdate
from app.models.visitor import Visitor
from app.models.user import User
from app.core.exceptions import AppException


class VisitorService(BaseService[Visitor]):
    """
    Domain Service for Visitor Registration, Duplicate Management, and Search/Filter Operations.
    """

    def __init__(self, db_session: AsyncSession):
        super().__init__(db_session)
        self.visitor_repo = VisitorRepository(db_session)

    async def register_visitor(self, payload: VisitorCreate, current_user: User) -> Visitor:
        # Check idempotent UUID
        existing_uuid = await self.visitor_repo.get_by_uuid(payload.visitor_uuid)
        if existing_uuid:
            return existing_uuid

        # Check if an active visitor with the same phone number exists today
        from fastapi import HTTPException, status
        from sqlalchemy import select
        from app.models.visitor import Visitor as VisitorModel

        p_res = await self.db.execute(
            select(VisitorModel).filter(
                VisitorModel.phone_number == payload.phone_number,
                VisitorModel.visitor_date == payload.visitor_date,
                VisitorModel.is_deleted.is_(False),
            )
        )
        existing_visitors = p_res.scalars().all()
        for ev in existing_visitors:
            is_checked_out = ev.notes and ("CHECKED_OUT" in ev.notes or "Visitor Left" in ev.notes)
            if not is_checked_out:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Visitor already inside temple."
                )

        data = payload.model_dump()
        data["volunteer_id"] = current_user.id
        data["sync_status"] = "SYNCED"

        if not data.get("purpose_id"):
            from sqlalchemy import select
            from app.models.purpose import Purpose
            p_res = await self.db.execute(select(Purpose.id).filter(Purpose.is_deleted.is_(False)))
            first_p = p_res.scalars().first()
            data["purpose_id"] = first_p or "3ef2daff-d716-4285-ac7c-81e702530b44"

        visitor = await self.visitor_repo.create(data, user_id=current_user.id)
        await self.commit()

        synced_visitor = await self.visitor_repo.get_by_uuid(visitor.visitor_uuid)

        # Trigger background ENTRY WhatsApp notification via CommunicationService
        try:
            from app.services.communication_service import CommunicationService
            comm_service = CommunicationService(self.db)
            await comm_service.prepare_and_record_message(
                visitor_id=synced_visitor.id,
                phone=synced_visitor.phone_number,
                message_type="ENTRY",
                context={
                    "name": synced_visitor.name,
                    "phone": synced_visitor.phone_number,
                    "date": str(synced_visitor.visitor_date),
                    "time": str(synced_visitor.visitor_time),
                    "duration": "N/A",
                    "visitor_id": synced_visitor.visitor_uuid,
                    "temple": "Sri Kalki Seva Alayam",
                    "volunteer": current_user.full_name or current_user.username,
                },
            )
        except Exception:
            # Async notification failures do not break visitor creation HTTP response
            pass

        # Broadcast real-time WebSocket event
        try:
            from app.core.websocket import websocket_manager
            from datetime import datetime, timezone
            await websocket_manager.broadcast_event(
                "VISITOR_REGISTERED",
                {
                    "visitor_id": str(synced_visitor.id),
                    "uuid": synced_visitor.visitor_uuid,
                    "name": synced_visitor.name,
                    "phone": synced_visitor.phone_number,
                    "persons_count": synced_visitor.persons_count,
                    "date": str(synced_visitor.visitor_date),
                    "time": str(synced_visitor.visitor_time),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            )
        from app.services.visitor_lifecycle import eval_visitor_lifecycle
        info = eval_visitor_lifecycle(synced_visitor)
        synced_visitor.status = info["status"]
        synced_visitor.is_auto_closed = info["is_auto_closed"]
        synced_visitor.check_in_time = info["check_in_time"]
        synced_visitor.check_out_time = info["check_out_time"]
        synced_visitor.duration = info["duration"]
        return synced_visitor

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
    ) -> Tuple[List[Visitor], int, int]:
        items, total = await self.visitor_repo.search_and_filter(
            search=search,
            purpose_id=purpose_id,
            village_id=village_id,
            date_from=date_from,
            date_to=date_to,
            volunteer_id=volunteer_id,
            page=page,
            limit=limit,
        )
        from app.services.visitor_lifecycle import eval_visitor_lifecycle
        for item in items:
            info = eval_visitor_lifecycle(item)
            item.status = info["status"]
            item.is_auto_closed = info["is_auto_closed"]
            item.check_in_time = info["check_in_time"]
            item.check_out_time = info["check_out_time"]
            item.duration = info["duration"]
        pages = ceil(total / limit) if total > 0 else 1
        return items, total, pages

    async def check_duplicate(self, name: str, phone_number: str, visitor_date: date) -> Optional[Visitor]:
        return await self.visitor_repo.check_duplicate(name=name, phone_number=phone_number, visitor_date=visitor_date)

    async def get_visitor_by_id(self, visitor_id: str) -> Visitor:
        visitor = await self.visitor_repo.get_by_id(visitor_id)
        if not visitor or visitor.is_deleted:
            raise AppException(status_code=404, detail="Visitor record not found", error_code="VISITOR_NOT_FOUND")
        from app.services.visitor_lifecycle import eval_visitor_lifecycle
        info = eval_visitor_lifecycle(visitor)
        visitor.status = info["status"]
        visitor.is_auto_closed = info["is_auto_closed"]
        visitor.check_in_time = info["check_in_time"]
        visitor.check_out_time = info["check_out_time"]
        visitor.duration = info["duration"]
        return visitor

    async def update_visitor(self, visitor_id: str, payload: VisitorUpdate, current_user: User) -> Visitor:
        visitor = await self.get_visitor_by_id(visitor_id)
        updated = await self.visitor_repo.update(visitor, payload.model_dump(exclude_unset=True), user_id=current_user.id)
        await self.commit()
        synced = await self.visitor_repo.get_by_uuid(updated.visitor_uuid)
        try:
            from app.core.websocket import websocket_manager
            from datetime import datetime, timezone
            await websocket_manager.broadcast_event(
                "VISITOR_UPDATED",
                {
                    "visitor_id": str(synced.id),
                    "uuid": synced.visitor_uuid,
                    "name": synced.name,
                    "phone": synced.phone_number,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            )
        except Exception:
            pass
        return synced

    async def delete_visitor(self, visitor_id: str, current_user: User) -> bool:
        visitor = await self.get_visitor_by_id(visitor_id)
        success = await self.visitor_repo.soft_delete(visitor.id, user_id=current_user.id)
        if success:
            await self.commit()
            try:
                from app.core.websocket import websocket_manager
                from datetime import datetime, timezone
                await websocket_manager.broadcast_event(
                    "VISITOR_DELETED",
                    {
                        "visitor_id": str(visitor_id),
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }
                )
            except Exception:
                pass
        return success

    async def checkout_visitor(self, visitor_uuid: str, checkout_time: Optional[str] = None, duration: Optional[str] = None, current_user: Optional[User] = None) -> Visitor:
        visitor = None
        try:
            visitor = await self.visitor_repo.get_by_uuid(visitor_uuid)
        except Exception:
            pass

        if not visitor:
            try:
                visitor = await self.visitor_repo.get_by_id(visitor_uuid)
            except Exception:
                pass

        if not visitor or visitor.is_deleted:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Visitor record not found")

        from datetime import datetime
        now_str = checkout_time or datetime.now().strftime("%H:%M:%S")
        dur_str = duration or "1 min"

        current_notes = visitor.notes or ""
        if "CHECKED_OUT" not in current_notes:
            checkout_tag = f"[CHECKED_OUT] Out: {now_str} ({dur_str})"
            new_notes = f"{current_notes} {checkout_tag}".strip() if current_notes else checkout_tag
        else:
            new_notes = current_notes

        updated = await self.visitor_repo.update(visitor, {"notes": new_notes}, user_id=current_user.id if current_user else None)
        await self.commit()

        try:
            from app.services.communication_service import CommunicationService
            comm_service = CommunicationService(self.db)
            await comm_service.prepare_and_record_message(
                visitor_id=updated.id,
                phone=updated.phone_number,
                message_type="EXIT",
                context={
                    "name": updated.name,
                    "phone": updated.phone_number,
                    "date": str(updated.visitor_date),
                    "time": str(now_str),
                    "duration": str(dur_str),
                    "visitor_id": updated.visitor_uuid,
                    "temple": "Sri Kalki Seva Alayam",
                    "volunteer": current_user.full_name or current_user.username if current_user else "Volunteer",
                },
            )
        except Exception:
            pass

        try:
            from app.core.websocket import websocket_manager
            from datetime import datetime, timezone
            await websocket_manager.broadcast_event(
                "VISITOR_CHECKED_OUT",
                {
                    "visitor_id": str(updated.id),
                    "uuid": updated.visitor_uuid,
                    "name": updated.name,
                    "phone": updated.phone_number,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            )
        from app.services.visitor_lifecycle import eval_visitor_lifecycle
        info = eval_visitor_lifecycle(updated)
        updated.status = info["status"]
        updated.is_auto_closed = info["is_auto_closed"]
        updated.check_in_time = info["check_in_time"]
        updated.check_out_time = info["check_out_time"]
        updated.duration = info["duration"]
        return updated
