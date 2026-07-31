from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models.user import User, Role, UserRole
from app.models.session import Session
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):

    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def get_by_username(self, username: str) -> Optional[User]:
        stmt = (
            select(User)
            .options(selectinload(User.roles).selectinload(Role.permissions))
            .filter(User.username == username, User.is_deleted.is_(False))
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_by_email(self, email: str) -> Optional[User]:
        stmt = (
            select(User)
            .options(selectinload(User.roles).selectinload(Role.permissions))
            .filter(User.email == email, User.is_deleted.is_(False))
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_by_id_with_relations(self, user_id: str) -> Optional[User]:
        stmt = (
            select(User)
            .options(selectinload(User.roles).selectinload(Role.permissions))
            .filter(User.id == str(user_id), User.is_deleted.is_(False))
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def assign_roles(self, user_id: str, role_ids: List[str]):
        # Clear existing
        stmt = select(UserRole).filter(UserRole.user_id == user_id)
        res = await self.session.execute(stmt)
        for r in res.scalars().all():
            await self.session.delete(r)

        # Assign new
        for role_id in role_ids:
            user_role = UserRole(user_id=user_id, role_id=role_id)
            self.session.add(user_role)
        await self.session.flush()


class SessionRepository(BaseRepository[Session]):

    def __init__(self, session: AsyncSession):
        super().__init__(Session, session)

    async def get_by_jti(self, token_jti: str) -> Optional[Session]:
        stmt = select(Session).filter(Session.token_jti == token_jti)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def revoke_session(self, token_jti: str) -> bool:
        session_entry = await self.get_by_jti(token_jti)
        if session_entry:
            session_entry.is_revoked = True
            self.session.add(session_entry)
            await self.session.flush()
            return True
        return False
