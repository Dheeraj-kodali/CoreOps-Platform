import time
import uuid
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

logger = logging.getLogger(__name__)


class AuditTracingMiddleware(BaseHTTPMiddleware):
    """
    Middleware generating unique request trace_id and measuring duration_ms.
    Attaches trace context to request.state and X-Trace-ID response header.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        trace_id = request.headers.get("X-Trace-ID", str(uuid.uuid4()))
        request.state.trace_id = trace_id
        start_time = time.perf_counter()

        response = await call_next(request)

        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
        request.state.duration_ms = duration_ms
        response.headers["X-Trace-ID"] = trace_id
        response.headers["X-Duration-MS"] = str(duration_ms)
        return response


class TenantIsolationMiddleware(BaseHTTPMiddleware):
    """
    Middleware extracting X-Temple-ID header or tenant scope from incoming requests,
    enforcing isolation context for multi-tenant deployments.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        temple_id = request.headers.get("X-Temple-ID", "SKSA_MAIN")
        request.state.temple_id = temple_id
        logger.debug(f"[Tenant Isolation] Active Temple ID set: {temple_id}")

        response = await call_next(request)
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware injecting security headers into every API response.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response
