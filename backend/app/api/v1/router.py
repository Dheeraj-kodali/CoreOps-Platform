from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth,
    users,
    roles,
    permissions,
    visitors,
    sync,
    notifications,
    analytics,
    reports,
    communication,
    settings,
    security,
    operations,
    ws,
)

api_router = APIRouter()

api_router.include_router(ws.router, tags=["WebSockets Real-Time"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(roles.router, prefix="/roles", tags=["Roles"])
api_router.include_router(permissions.router, prefix="/permissions", tags=["Permissions"])
api_router.include_router(visitors.router, prefix="/visitors", tags=["Visitors"])
api_router.include_router(sync.router, prefix="/sync", tags=["Offline Sync Engine"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(reports.router, prefix="/reports", tags=["Reports Export"])
api_router.include_router(communication.router, prefix="/communication", tags=["Communication"])
api_router.include_router(settings.router, prefix="/settings", tags=["Temple Settings"])
api_router.include_router(security.router, prefix="/security", tags=["Security Center"])
api_router.include_router(operations.router, prefix="/operations", tags=["Operations Center"])
