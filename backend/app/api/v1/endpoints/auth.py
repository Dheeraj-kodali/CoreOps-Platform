from fastapi import APIRouter, Depends, Request, status, HTTPException
from app.api.deps import get_current_user, get_auth_service
from app.schemas.token import Token, RefreshTokenRequest, ForgotPasswordRequest, ResetPasswordRequest
from app.schemas.user import LoginRequest, UserResponse
from app.models.user import User
from app.services.auth_service import AuthService
from app.core.security import decode_token, create_access_token, create_refresh_token, create_password_reset_token, validate_password_policy, get_password_hash
from app.repositories.user_repository import UserRepository, SessionRepository
from app.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone, timedelta
from app.core.config import settings
from app.models.session import Session

router = APIRouter()


@router.post("/login", response_model=Token)
async def login(
    request_data: LoginRequest,
    req: Request,
    auth_service: AuthService = Depends(get_auth_service)
):
    client_ip = req.client.host if req.client else "127.0.0.1"
    user_agent = req.headers.get("user-agent", "Unknown")
    result = await auth_service.authenticate_user(
        username=request_data.username,
        password=request_data.password,
        ip_address=client_ip,
        user_agent=user_agent
    )
    return Token(access_token=result["access_token"], refresh_token=result["refresh_token"])


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    jti = getattr(current_user, "current_jti", None)
    if jti:
        await auth_service.logout_user(jti)
    return {"message": "Successfully logged out"}


@router.post("/refresh", response_model=Token)
async def refresh_token(payload_data: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    payload = decode_token(payload_data.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    jti = payload.get("jti")
    user_id = payload.get("sub")

    session_repo = SessionRepository(db)
    session_entry = await session_repo.get_by_jti(jti)
    if not session_entry or session_entry.is_revoked:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session revoked or invalid")

    user_repo = UserRepository(db)
    user = await user_repo.get_by_id_with_relations(user_id)
    if not user or not user.is_active or user.is_deleted:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User account unavailable")

    new_access_token = create_access_token(subject=user.id, jti=jti)
    new_refresh_token = create_refresh_token(subject=user.id, jti=jti)

    session_entry.is_revoked = True
    db.add(session_entry)

    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    new_session = Session(
        user_id=user.id,
        token_jti=jti,
        refresh_token=new_refresh_token,
        ip_address=session_entry.ip_address,
        user_agent=session_entry.user_agent,
        expires_at=expires_at,
        is_revoked=False,
    )
    db.add(new_session)
    await db.commit()

    return Token(access_token=new_access_token, refresh_token=new_refresh_token)


@router.post("/forgot-password")
async def forgot_password(data: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    user_repo = UserRepository(db)
    user = await user_repo.get_by_username(data.username_or_email)
    if not user:
        user = await user_repo.get_by_email(data.username_or_email)

    if user:
        reset_token = create_password_reset_token(subject=user.id)
        return {"message": "Password reset token generated", "reset_token": reset_token}
    return {"message": "If an account exists, a password reset token has been issued"}


@router.post("/reset-password")
async def reset_password(data: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    payload = decode_token(data.reset_token)
    if not payload or payload.get("type") != "reset_password":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired reset token")

    valid_pw, msg = validate_password_policy(data.new_password)
    if not valid_pw:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)

    user_id = payload.get("sub")
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)
    if not user or user.is_deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.password_hash = get_password_hash(data.new_password)
    db.add(user)
    await db.commit()
    return {"message": "Password reset successfully"}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
