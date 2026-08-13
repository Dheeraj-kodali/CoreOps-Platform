from datetime import date, datetime, timedelta, timezone
from typing import Optional, Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select, or_
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.visitor import Visitor
from app.models.visit_session import VisitSession
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
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)
    year_start = today.replace(month=1, day=1)

    # Queries
    today_q = await db.execute(select(func.count(Visitor.id)).filter(Visitor.visitor_date == today, Visitor.is_deleted.is_(False)))
    weekly_q = await db.execute(select(func.count(Visitor.id)).filter(Visitor.visitor_date >= week_start, Visitor.is_deleted.is_(False)))
    monthly_q = await db.execute(select(func.count(Visitor.id)).filter(Visitor.visitor_date >= month_start, Visitor.is_deleted.is_(False)))
    yearly_q = await db.execute(select(func.count(Visitor.id)).filter(Visitor.visitor_date >= year_start, Visitor.is_deleted.is_(False)))
    total_q = await db.execute(select(func.count(Visitor.id)).filter(Visitor.is_deleted.is_(False)))

    # Live stats
    one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
    last_hour_q = await db.execute(select(func.count(Visitor.id)).filter(Visitor.created_at >= one_hour_ago, Visitor.is_deleted.is_(False)))
    pending_sync_q = await db.execute(select(func.count(SyncQueue.id)).filter(SyncQueue.status == "PENDING"))
    active_volunteers_q = await db.execute(select(func.count(User.id)).filter(User.is_active, User.is_deleted.is_(False)))

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


@router.get("/dashboard")
async def get_admin_dashboard(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    today = date.today()
    
    # 1. Total visitors today (check VisitSession first, fallback to Visitor)
    vs_res = await db.execute(
        select(func.coalesce(func.sum(VisitSession.persons_count), 0)).filter(
            VisitSession.visit_date == today, VisitSession.is_deleted.is_(False)
        )
    )
    vs_count = vs_res.scalar_one()

    today_v_res = await db.execute(
        select(func.coalesce(func.sum(Visitor.persons_count), 0)).filter(
            Visitor.visitor_date == today, Visitor.is_deleted.is_(False)
        )
    )
    v_count = today_v_res.scalar_one()
    todays_visitors = vs_count if vs_count > 0 else v_count

    # Total check-in records today
    vs_checkins = await db.execute(
        select(func.count(VisitSession.id)).filter(
            VisitSession.visit_date == today, VisitSession.is_deleted.is_(False)
        )
    )
    v_checkins = await db.execute(
        select(func.count(Visitor.id)).filter(
            Visitor.visitor_date == today, Visitor.is_deleted.is_(False)
        )
    )
    todays_check_ins = vs_checkins.scalar_one() or v_checkins.scalar_one()

    display_visitors = todays_visitors
    display_checkins = todays_check_ins

    # Total check-outs for today (check VisitSession status == CHECKED_OUT first, fallback to Visitor notes)
    vs_checkouts_res = await db.execute(
        select(func.coalesce(func.sum(VisitSession.persons_count), 0)).filter(
            VisitSession.visit_date == today,
            VisitSession.status == "CHECKED_OUT",
            VisitSession.is_deleted.is_(False),
        )
    )
    vs_checkouts = vs_checkouts_res.scalar_one()

    checkouts_res = await db.execute(
        select(func.coalesce(func.sum(Visitor.persons_count), 0)).filter(
            Visitor.visitor_date == today,
            Visitor.is_deleted.is_(False),
            or_(
                Visitor.notes.like("%CHECKED_OUT%"),
                Visitor.notes.like("%Visitor Left%"),
                Visitor.notes.like("%Exit Time%"),
            )
        )
    )
    v_checkouts = checkouts_res.scalar_one()
    todays_check_outs = vs_checkouts if vs_checkouts > 0 else v_checkouts

    # Real calculation of visitors inside premise today
    visitors_inside = max(0, display_visitors - todays_check_outs)

    # Pending sync queue items
    pending_sync_res = await db.execute(
        select(func.count(SyncQueue.id)).filter(SyncQueue.status == "PENDING")
    )
    pending_sync = pending_sync_res.scalar_one()

    # Recent Visitors (latest 10)
    recent_res = await db.execute(
        select(Visitor).filter(Visitor.is_deleted.is_(False)).order_by(Visitor.created_at.desc()).limit(10)
    )
    recent_visitors_list = recent_res.scalars().all()

    # Purpose breakdown for charts
    purpose_res = await db.execute(
        select(Purpose.name_en, func.count(Visitor.id).label("count"))
        .select_from(Purpose)
        .join(Visitor, Visitor.purpose_id == Purpose.id)
        .filter(Visitor.is_deleted.is_(False))
        .group_by(Purpose.name_en, Purpose.id)
    )
    rows = purpose_res.all()
    if rows:
        total_p = sum(r.count for r in rows)
        purpose_breakdown = [
            {
                "name": r.name_en,
                "count": r.count,
                "percentage": round((r.count / total_p * 100), 1) if total_p > 0 else 0,
            }
            for r in rows
        ]
    else:
        purpose_breakdown = [
            {"name": "General Darshan", "count": display_checkins, "percentage": 100.0}
        ]

    from app.services.visitor_lifecycle import eval_visitor_lifecycle

    recent_visitor_dtos = []
    for v in recent_visitors_list:
        info = eval_visitor_lifecycle(v, current_date=today)
        recent_visitor_dtos.append({
            "id": str(v.id),
            "uuid": v.visitor_uuid,
            "name": v.name,
            "phone": v.phone_number,
            "persons_count": v.persons_count,
            "date": str(v.visitor_date),
            "time": str(v.visitor_time),
            "status": info["status"],
            "is_auto_closed": info["is_auto_closed"],
            "check_in_time": info["check_in_time"],
            "check_out_time": info["check_out_time"],
            "duration": info["duration"],
        })

    return {
        "todays_visitors": display_visitors,
        "visitors_inside": visitors_inside,
        "todays_check_ins": display_checkins,
        "todays_check_outs": todays_check_outs,
        "pending_sync": pending_sync,
        "broadcast_status": "Active",
        "recent_visitors": recent_visitor_dtos,
        "purpose_breakdown": purpose_breakdown,
        "system_health": {
            "api_status": "ONLINE",
            "db_status": "CONNECTED",
            "offline_sync_engine": "ACTIVE",
        }
    }


@router.get("/purpose-breakdown", response_model=PurposeAnalyticsResponse)
async def get_purpose_breakdown(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    db: Annotated[AsyncSession, Depends(get_db)] = None,
    current_user: Annotated[User, Depends(get_current_user)] = None,
):
    stmt = (
        select(Purpose.id, Purpose.name_en, Purpose.name_te, func.count(Visitor.id).label("count"))
        .join(Visitor, Visitor.purpose_id == Purpose.id)
        .filter(Visitor.is_deleted.is_(False))
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
