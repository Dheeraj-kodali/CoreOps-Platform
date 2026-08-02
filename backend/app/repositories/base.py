from datetime import datetime, timezone
from typing import Generic, TypeVar, Type, Optional, List, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):

    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def get_by_id(self, id: Any, include_deleted: bool = False) -> Optional[ModelType]:
        stmt = select(self.model).filter(self.model.id == str(id))
        if hasattr(self.model, "is_deleted") and not include_deleted:
            stmt = stmt.filter(self.model.is_deleted.is_(False))
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_all(self, skip: int = 0, limit: int = 100, include_deleted: bool = False) -> List[ModelType]:
        stmt = select(self.model)
        if hasattr(self.model, "is_deleted") and not include_deleted:
            stmt = stmt.filter(self.model.is_deleted.is_(False))
        stmt = stmt.offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count(self, include_deleted: bool = False) -> int:
        stmt = select(func.count()).select_from(self.model)
        if hasattr(self.model, "is_deleted") and not include_deleted:
            stmt = stmt.filter(self.model.is_deleted.is_(False))
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def create(self, obj_in: dict, user_id: Optional[str] = None) -> ModelType:
        if hasattr(self.model, "created_by") and user_id:
            obj_in["created_by"] = user_id
        excluded_keys = {"status", "is_auto_closed", "check_in_time", "check_out_time", "duration"}
        clean_obj = {k: v for k, v in obj_in.items() if not k.startswith('_') and k not in excluded_keys}
        db_obj = self.model(**clean_obj)
        self.session.add(db_obj)
        await self.session.flush()
        await self.session.refresh(db_obj)
        return db_obj

    async def update(self, db_obj: ModelType, obj_in: dict, user_id: Optional[str] = None) -> ModelType:
        if hasattr(db_obj, "updated_by") and user_id:
            setattr(db_obj, "updated_by", user_id)
        for field, value in obj_in.items():
            if hasattr(db_obj, field) and value is not None:
                setattr(db_obj, field, value)
        self.session.add(db_obj)
        await self.session.flush()
        await self.session.refresh(db_obj)
        return db_obj

    async def soft_delete(self, id: Any, user_id: Optional[str] = None) -> bool:
        db_obj = await self.get_by_id(id)
        if db_obj:
            if hasattr(db_obj, "is_deleted"):
                setattr(db_obj, "is_deleted", True)
                setattr(db_obj, "deleted_at", datetime.now(timezone.utc))
                if user_id and hasattr(db_obj, "updated_by"):
                    setattr(db_obj, "updated_by", user_id)
                self.session.add(db_obj)
                await self.session.flush()
                return True
        return False
