from typing import Optional, Callable
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.database import get_db
from app.core.security import decode_token
from app.models.user import User
from app.repositories.user_repository import UserRepository, SessionRepository
from app.services.visitor_service import VisitorService
from app.services.sync_service import SyncService
from app.services.auth_service import AuthService
from app.services.communication_service import CommunicationService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials or active session",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        raise credentials_exception

    user_id: Optional[str] = payload.get("sub")
    jti: Optional[str] = payload.get("jti")
    if not user_id or not jti:
        raise credentials_exception

    # Session active check
    session_repo = SessionRepository(db)
    active_session = await session_repo.get_by_jti(jti)
    if not active_session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired or logged out",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_repo = UserRepository(db)
    user = await user_repo.get_by_id_with_relations(user_id)
    if not user or user.is_deleted:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user account")

    user.current_jti = jti
    return user


def require_permission(permission_code: str) -> Callable:
    async def permission_checker(current_user: User = Depends(get_current_user)) -> User:
        user_role_names = [r.name for r in current_user.roles]
        if "SUPER_ADMIN" in user_role_names:
            return current_user

        user_permission_codes = []
        for r in current_user.roles:
            user_permission_codes.extend([p.code for p in r.permissions])

        if permission_code not in user_permission_codes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission_code}' required for this action",
            )
        return current_user

    return permission_checker


# Dependency Injection Service Providers
async def get_visitor_service(db: AsyncSession = Depends(get_db)) -> VisitorService:
    return VisitorService(db)


async def get_sync_service(db: AsyncSession = Depends(get_db)) -> SyncService:
    return SyncService(db)


async def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(db)


async def get_communication_service(db: AsyncSession = Depends(get_db)) -> CommunicationService:
    return CommunicationService(db)
