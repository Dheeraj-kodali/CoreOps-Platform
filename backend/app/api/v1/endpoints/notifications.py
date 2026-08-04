from typing import Annotated, List
from math import ceil
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from app.core.database import get_db
from app.api.deps import get_current_user, require_permission
from app.models.user import User
from app.models.notification import NotificationTemplate, NotificationLog
from app.schemas.notification import (
    NotificationTemplateResponse,
    NotificationLogListResponse,
)

router = APIRouter()


@router.get("/templates", response_model=List[NotificationTemplateResponse])
async def list_templates(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    stmt = select(NotificationTemplate)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/logs", response_model=NotificationLogListResponse)
async def list_logs(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    stmt = select(NotificationLog).order_by(NotificationLog.created_at.desc())
    count_stmt = select(func.count(NotificationLog.id))

    total_res = await db.execute(count_stmt)
    total = total_res.scalar_one()

    offset = (page - 1) * limit
    stmt = stmt.offset(offset).limit(limit)

    res = await db.execute(stmt)
    items = res.scalars().all()

    pages = ceil(total / limit) if total > 0 else 1
    return NotificationLogListResponse(items=items, total=total, page=page, limit=limit, pages=pages)


@router.post("/logs/{log_id}/retry")
async def retry_notification(
    log_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission("notifications:manage"))],
):
    stmt = select(NotificationLog).filter(NotificationLog.id == log_id)
    res = await db.execute(stmt)
    log_entry = res.scalars().first()

    if not log_entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification log not found")

    log_entry.status = "PENDING"
    log_entry.retry_count = (log_entry.retry_count or 0) + 1
    db.add(log_entry)
    await db.commit()

    # In production, dispatch task to Celery queue here
    return {"message": "Notification queued for retry", "status": "PENDING", "log_id": log_id}
