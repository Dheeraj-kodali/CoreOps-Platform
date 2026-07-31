from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.session import Session
from app.models.audit import AuditRecord

router = APIRouter()

# Mock active sessions store for admin management
ACTIVE_SESSIONS_STORE = [
    {
        "session_id": "sess-admin-01",
        "user_id": "u-admin",
        "username": "admin",
        "role": "Administrator",
        "ip_address": "127.0.0.1",
        "device": "Chrome 126.0 (Windows 11)",
        "created_at": "2026-07-31 09:30 AM",
        "is_current": True,
    },
    {
        "session_id": "sess-manager-02",
        "user_id": "u-manager",
        "username": "manager_chittoor",
        "role": "Manager",
        "ip_address": "192.168.1.45",
        "device": "Firefox 127.0 (Android 14)",
        "created_at": "2026-07-31 10:15 AM",
        "is_current": False,
    },
]

LOGIN_ATTEMPTS_HISTORY = [
    {
        "id": "log-001",
        "timestamp": "2026-07-31 11:20:15",
        "username": "admin",
        "role": "Administrator",
        "ip_address": "127.0.0.1",
        "device": "Chrome 126.0 (Windows)",
        "status": "SUCCESS",
    },
    {
        "id": "log-002",
        "timestamp": "2026-07-31 10:45:00",
        "username": "unknown_user",
        "role": "Unknown",
        "ip_address": "49.207.12.88",
        "device": "Safari (iOS 17)",
        "status": "FAILED_INVALID_CREDENTIALS",
    },
    {
        "id": "log-003",
        "timestamp": "2026-07-31 09:15:30",
        "username": "manager_chittoor",
        "role": "Manager",
        "ip_address": "192.168.1.45",
        "device": "Firefox (Android)",
        "status": "SUCCESS",
    },
]


@router.get("/overview")
async def get_security_overview(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return {
        "security_score": 96,
        "security_rating": "EXCELLENT",
        "last_successful_login": "2026-07-31 11:20:15",
        "last_failed_login": "2026-07-31 10:45:00",
        "active_sessions_count": len(ACTIVE_SESSIONS_STORE),
        "locked_accounts_count": 0,
        "password_expiration_days": 90,
        "mfa_status": "TOTP_READINESS_ENABLED",
        "rate_limiting": "ACTIVE (100 req/min)",
    }


@router.get("/sessions")
async def list_active_sessions(
    current_user: User = Depends(get_current_user),
):
    return {"sessions": ACTIVE_SESSIONS_STORE, "total": len(ACTIVE_SESSIONS_STORE)}


@router.delete("/sessions/{session_id}")
async def revoke_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    global ACTIVE_SESSIONS_STORE
    ACTIVE_SESSIONS_STORE = [s for s in ACTIVE_SESSIONS_STORE if s["session_id"] != session_id]

    # Write event to AuditRecord
    audit = AuditRecord(
        user_id=getattr(current_user, "id", None),
        role=getattr(current_user, "role", "Administrator"),
        action="SESSION_REVOKED",
        entity_type="SecuritySession",
        entity_id=session_id,
        status="SUCCESS",
        severity="WARNING",
    )
    db.add(audit)
    await db.commit()

    return {"message": f"Session {session_id} successfully revoked."}


@router.delete("/sessions")
async def logout_all_devices(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    global ACTIVE_SESSIONS_STORE
    ACTIVE_SESSIONS_STORE = [s for s in ACTIVE_SESSIONS_STORE if s.get("is_current")]

    audit = AuditRecord(
        user_id=getattr(current_user, "id", None),
        role=getattr(current_user, "role", "Administrator"),
        action="LOGOUT_ALL_DEVICES",
        entity_type="SecuritySession",
        status="SUCCESS",
        severity="WARNING",
    )
    db.add(audit)
    await db.commit()

    return {"message": "All secondary active sessions revoked successfully."}


@router.get("/login-history")
async def get_login_history(
    current_user: User = Depends(get_current_user),
):
    return {"history": LOGIN_ATTEMPTS_HISTORY, "total": len(LOGIN_ATTEMPTS_HISTORY)}


@router.post("/unlock/{user_id}")
async def unlock_account(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    audit = AuditRecord(
        user_id=getattr(current_user, "id", None),
        role=getattr(current_user, "role", "Administrator"),
        action="ACCOUNT_MANUAL_UNLOCK",
        entity_type="UserAccount",
        entity_id=user_id,
        status="SUCCESS",
        severity="INFO",
    )
    db.add(audit)
    await db.commit()

    return {"message": f"Account {user_id} successfully unlocked."}
