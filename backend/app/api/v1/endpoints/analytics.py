from datetime import date, datetime, timedelta, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.visitor import Visitor
from app.models.purpose import Purpose
from app.models.sync import SyncQueue
from app.schemas.analytics import (
    DashboardSummaryResponse,
    LiveStatistics,
    PurposeAnalyticsResponse,
    PurposeAnalyticsItem,
)

router = APIRouter()


@router.get("/summary", response_model=DashboardSummaryResponse)
async def get_dashboard_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)
    year_start = today.replace(month=1, day=1)

    # Queries
    today_q = await db.execute(select(func.count(Visitor.id)).filter(Visitor.visitor_date == today))
    weekly_q = await db.execute(select(func.count(Visitor.id)).filter(Visitor.visitor_date >= week_start))
    monthly_q = await db.execute(select(func.count(Visitor.id)).filter(Visitor.visitor_date >= month_start))
    yearly_q = await db.execute(select(func.count(Visitor.id)).filter(Visitor.visitor_date >= year_start))
    total_q = await db.execute(select(func.count(Visitor.id)))

    # Live stats
    one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
    last_hour_q = await db.execute(select(func.count(Visitor.id)).filter(Visitor.created_at >= one_hour_ago))
    pending_sync_q = await db.execute(select(func.count(SyncQueue.id)).filter(SyncQueue.status == "PENDING"))
    active_volunteers_q = await db.execute(select(func.count(User.id)).filter(User.is_active))

    return DashboardSummaryResponse(
        today_visitors=today_q.scalar_one(),
        weekly_visitors=weekly_q.scalar_one(),
        monthly_visitors=monthly_q.scalar_one(),
        yearly_visitors=yearly_q.scalar_one(),
        total_visitors=total_q.scalar_one(),
        live_statistics=LiveStatistics(
            active_volunteers=active_volunteers_q.scalar_one(),
            visitors_last_hour=last_hour_q.scalar_one(),
            pending_sync_queue=pending_sync_q.scalar_one(),
        ),
    )


@router.get("/purpose-breakdown", response_model=PurposeAnalyticsResponse)
async def get_purpose_breakdown(
    date_from: str = None,
    date_to: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = (
        select(Purpose.id, Purpose.name_en, Purpose.name_te, func.count(Visitor.id).label("count"))
        .join(Visitor, Visitor.purpose_id == Purpose.id)
        .group_by(Purpose.id, Purpose.name_en, Purpose.name_te)
    )

    result = await db.execute(stmt)
    rows = result.all()

    total = sum(row.count for row in rows)
    breakdown = []
    for row in rows:
        pct = round((row.count / total * 100), 2) if total > 0 else 0.0
        breakdown.append(
            PurposeAnalyticsItem(
                purpose_id=row.id,
                name_en=row.name_en,
                name_te=row.name_te,
                count=row.count,
                percentage=pct,
            )
        )

    return PurposeAnalyticsResponse(total=total, breakdown=breakdown)
