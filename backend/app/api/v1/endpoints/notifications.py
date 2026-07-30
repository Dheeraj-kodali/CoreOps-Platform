from typing import List
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
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = select(NotificationTemplate)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/logs", response_model=NotificationLogListResponse)
async def list_logs(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
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
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("notifications:manage")),
):
    stmt = select(NotificationLog).filter(NotificationLog.id == log_id)
    res = await db.execute(stmt)
    log_entry = res.scalars().first()

    if not log_entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Log entry not found")

    log_entry.status = "PENDING"
    log_entry.retry_count += 1
    await db.commit()

    # In production, dispatch task to Celery queue here
    return {"message": "Notification retry queued successfully", "log_id": log_id}
