from fastapi import APIRouter
from app.api.v2.endpoints import health, auth, sync, audit, dashboard, broadcast

api_v2_router = APIRouter()

api_v2_router.include_router(health.router, tags=["Health v2"])
api_v2_router.include_router(auth.router, prefix="/auth", tags=["Auth v2"])
api_v2_router.include_router(sync.router, prefix="/sync", tags=["Sync v2"])
api_v2_router.include_router(audit.router, prefix="/audit", tags=["Audit v2"])
api_v2_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard v2"])
api_v2_router.include_router(broadcast.router, prefix="/broadcast", tags=["Broadcast v2"])
