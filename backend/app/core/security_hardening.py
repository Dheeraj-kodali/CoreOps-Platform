import time
import logging
from typing import Dict, Tuple, Optional
from fastapi import Header, HTTPException, status
from sqlalchemy.future import select

from app.core.database import AsyncSessionLocal
from app.models.device import Device
from app.core.audit_hook import record_audit_event

logger = logging.getLogger(__name__)

# Default Master API Key for system-to-system integration
SYSTEM_API_KEY = "sk_temple_v2_prod_998877665544"


class InMemoryRateLimiter:
    """Token Bucket & Window Rate Limiter for API Security Hardening."""

    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.client_records: Dict[str, Tuple[int, float]] = {}

    def is_rate_limited(self, client_id: str) -> bool:
        now = time.time()
        if client_id not in self.client_records:
            self.client_records[client_id] = (1, now)
            return False

        count, first_time = self.client_records[client_id]
        if now - first_time > self.window_seconds:
            self.client_records[client_id] = (1, now)
            return False

        if count >= self.max_requests:
            return True

        self.client_records[client_id] = (count + 1, first_time)
        return False


rate_limiter = InMemoryRateLimiter(max_requests=120, window_seconds=60)


async def validate_api_key(x_api_key: Optional[str] = Header(None, alias="X-API-Key")):
    """Dependency verifying X-API-Key header for machine-to-machine integrations."""
    if not x_api_key:
        return True  # Optional API key for standard user JWT flows

    if x_api_key != SYSTEM_API_KEY:
        logger.warning(f"SecurityHardening: Invalid API Key attempt: {x_api_key[:4]}...")
        async with AsyncSessionLocal() as session:
            await record_audit_event(
                session,
                action="UNAUTHORIZED_ACCESS_ATTEMPT",
                entity_type="SECURITY",
                entity_id="API_KEY_VALIDATION",
                severity="WARNING",
                reason=f"Invalid API Key presented: {x_api_key[:4]}...",
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key presented.",
        )
    return True


async def verify_device_registration(device_id: str, temple_id: str = "SKSA_MAIN") -> bool:
    """Verifies that a mobile tablet kiosk or admin device is registered and active."""
    if not device_id:
        return False

    async with AsyncSessionLocal() as session:
        stmt = select(Device).filter(Device.device_id == device_id, Device.temple_id == temple_id)
        res = await session.execute(stmt)
        dev = res.scalars().first()
        if not dev or getattr(dev, "status", "ACTIVE") != "ACTIVE":
            return False
        return True


async def log_security_event(
    action: str,
    reason: str,
    user_id: Optional[str] = None,
    temple_id: str = "SKSA_MAIN",
    severity: str = "WARNING",
):
    """Helper to emit structured security audit events."""
    async with AsyncSessionLocal() as session:
        await record_audit_event(
            session,
            action=action,
            entity_type="SECURITY",
            entity_id=user_id or "ANONYMOUS",
            user_id=user_id,
            temple_id=temple_id,
            severity=severity,
            reason=reason,
        )
