from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.config import settings
from app.core.security import verify_password, create_access_token, create_refresh_token, decode_token
from app.core.audit_hook import record_audit_event
from app.core.rbac import ROLE_PERMISSIONS_MATRIX
from app.models.user import User, Role
from app.models.session import Session as UserSession
from app.schemas.auth_v2 import (
    V2LoginRequest, V2TokenResponse, V2RefreshTokenRequest,
    V2RefreshTokenResponse, V2UserProfileResponse
)
from app.api.deps import get_current_user

router = APIRouter()


@router.post("/login", response_model=V2TokenResponse)
async def login_v2(
    login_data: V2LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """v2 API Authentication Endpoint.
    
    Authenticates user, creates session record, and issues Bearer access & refresh tokens.
    """
    res = await db.execute(
        select(User)
        .options(selectinload(User.roles).selectinload(Role.permissions))
        .filter(User.username == login_data.username, User.is_deleted.is_(False))
    )
    user = res.scalars().first()

    if not user or not verify_password(login_data.password, user.password_hash):
        await record_audit_event(
            db, action="USER_LOGIN_FAILED", resource="auth",
            user_id=user.id if user else None,
            result="FAILURE", ip_address=request.client.host if request.client else None,
            reason="Invalid credentials"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user account")

    # Generate JWT Tokens
    access_token, jti = create_access_token(subject=user.id)
    refresh_token, _ = create_refresh_token(subject=user.id, jti=jti)

    # Persist active Session
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    session_record = UserSession(
        user_id=user.id,
        token_jti=jti,
        refresh_token=refresh_token,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        expires_at=expires_at,
    )
    db.add(session_record)
    await db.commit()

    # Record Audit Event
    temple_id = getattr(request.state, "temple_id", "SKSA_MAIN")
    await record_audit_event(
        db, action="USER_LOGIN", resource="auth",
        user_id=user.id, temple_id=temple_id,
        role=user.roles[0].name if user.roles else "USER",
        ip_address=request.client.host if request.client else None,
        result="SUCCESS"
    )

    return V2TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/refresh", response_model=V2RefreshTokenResponse)
async def refresh_token_v2(
    refresh_data: V2RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    """v2 Refresh Token Renewal Endpoint."""
    payload = decode_token(refresh_data.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    user_id = payload.get("sub")
    jti = payload.get("jti")

    res = await db.execute(
        select(UserSession).filter(
            UserSession.token_jti == jti,
            UserSession.is_revoked.is_(False)
        )
    )
    session = res.scalars().first()
    if not session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Revoked or expired session")

    new_access_token, _ = create_access_token(subject=user_id, jti=jti)
    return V2RefreshTokenResponse(
        access_token=new_access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.get("/me", response_model=V2UserProfileResponse)
async def get_me_v2(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    """v2 Profile & RBAC Permissions Endpoint."""
    user_roles = [r.name for r in current_user.roles]
    permissions_set = set()

    for role_name in user_roles:
        perms = ROLE_PERMISSIONS_MATRIX.get(role_name, set())
        permissions_set.update(perms)

    temple_id = getattr(request.state, "temple_id", "SKSA_MAIN")

    return V2UserProfileResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        phone_number=current_user.phone_number,
        temple_id=temple_id,
        is_active=current_user.is_active,
        roles=user_roles,
        permissions=list(permissions_set),
    )


@router.post("/logout")
async def logout_v2(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """v2 Session Revocation Endpoint."""
    jti = getattr(current_user, "current_jti", None)
    if jti:
        res = await db.execute(select(UserSession).filter(UserSession.token_jti == jti))
        session = res.scalars().first()
        if session:
            session.is_revoked = True
            await db.commit()

    await record_audit_event(
        db, action="USER_LOGOUT", resource="auth",
        user_id=current_user.id, result="SUCCESS",
        ip_address=request.client.host if request.client else None
    )
    return {"message": "Successfully logged out"}
