from datetime import datetime, timezone, timedelta
import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.base_service import BaseService
from app.repositories.user_repository import UserRepository, SessionRepository
from app.core.security import verify_password, create_access_token, create_refresh_token
from app.core.config import settings
from app.core.exceptions import AuthenticationException
from app.core.events import event_bus, UserLoggedInEvent
from app.models.user import User


class AuthService(BaseService[User]):
    """
    Domain Service for User Authentication, Token Rotation, Session Tracking,
    and Login Security Auditing.
    """

    def __init__(self, db_session: AsyncSession):
        super().__init__(db_session)
        self.user_repo = UserRepository(db_session)
        self.session_repo = SessionRepository(db_session)

    async def authenticate_user(self, username: str, password: str, ip_address: Optional[str] = None, user_agent: Optional[str] = None) -> dict:
        user = await self.user_repo.get_by_username(username)
        if not user or user.is_deleted or not verify_password(password, user.password_hash):
            raise AuthenticationException(detail="Invalid username or password")

        if not user.is_active:
            raise AuthenticationException(detail="User account is inactive")

        # Generate unique JWT token identifier (JTI)
        token_jti = str(uuid.uuid4())

        # Access & Refresh Tokens
        access_token, _ = create_access_token(
            subject=user.id,
            jti=token_jti,
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        refresh_token, _ = create_refresh_token(
            subject=user.id,
            jti=token_jti,
            expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        )

        # Create active user session record
        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        await self.session_repo.create({
            "user_id": user.id,
            "token_jti": token_jti,
            "refresh_token": refresh_token,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "is_revoked": False,
            "expires_at": expires_at,
        })
        await self.commit()

        # Publish UserLoggedInEvent to Domain Event Bus
        await event_bus.publish(UserLoggedInEvent(user_id=user.id, username=user.username, ip_address=ip_address))

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }

    async def logout_user(self, jti: str) -> bool:
        session = await self.session_repo.get_by_jti(jti)
        if session:
            session.is_revoked = True
            await self.commit()
            return True
        return False
