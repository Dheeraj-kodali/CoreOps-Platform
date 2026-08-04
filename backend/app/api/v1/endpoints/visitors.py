from datetime import date
from typing import Annotated, Optional, List
from pydantic import BaseModel
from fastapi import APIRouter, Depends, Query, status, HTTPException, Body

from app.api.deps import get_current_user, require_permission, get_visitor_service
from app.models.user import User
from app.services.visitor_service import VisitorService
from app.schemas.visitor import (
    VisitSessionCreate, VisitorProfileUpdate, VisitorResponse, VisitorListResponse,
    PhoneLookupResponse, VisitorProfileResponse, VisitorUpdate,
    DailyLedgerResponse, DailyLedgerListResponse, DailyLedgerSummary,
    PurposeResponse, VillageResponse
)

router = APIRouter()


class BulkDeleteRequest(BaseModel):
    visitor_ids: List[str]


class VisitorCheckoutRequest(BaseModel):
    checkout_time: Optional[str] = None
    duration: Optional[str] = None


@router.get("/lookup-phone", response_model=PhoneLookupResponse)
async def lookup_phone(
    service: Annotated[VisitorService, Depends(get_visitor_service)],
    current_user: Annotated[User, Depends(get_current_user)],
    phone_number: Annotated[str, Query(min_length=5, max_length=20)],
):
    """
    Search Visitor Profile by Phone Number for Reception Auto-Fill Flow.
    Returns profile information + last visit summary if profile exists.
    """
    return await service.lookup_phone(phone_number)


@router.post("/", response_model=VisitorResponse, status_code=status.HTTP_201_CREATED)
async def create_visitor(
    payload: VisitSessionCreate,
    service: Annotated[VisitorService, Depends(get_visitor_service)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Visitor Entry Flow:
    - If profile exists: reuses profile, creates ONLY a new Visit Session.
    - If profile does NOT exist: creates Visitor Profile + first Visit Session.
    """
    session_record = await service.register_visitor(payload, current_user)
    return _map_session_to_visitor_response(session_record)


@router.put("/profiles/{profile_id}", response_model=VisitorProfileResponse)
async def update_visitor_profile(
    profile_id: str,
    payload: VisitorProfileUpdate,
    service: Annotated[VisitorService, Depends(get_visitor_service)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Edit Profile Functionality:
    Modifies permanent Visitor Profile fields only. Past Visit Sessions remain unchanged.
    """
    updated_profile = await service.update_profile(profile_id, payload, current_user)
    return VisitorProfileResponse.model_validate(updated_profile)


def _map_session_to_visitor_response(session_record) -> VisitorResponse:
    prof = session_record.visitor_profile
    purpose_resp = PurposeResponse.model_validate(session_record.purpose) if session_record and session_record.purpose else None
    village_resp = VillageResponse.model_validate(prof.village) if prof and prof.village else None

    return VisitorResponse(
        id=session_record.id,
        visitor_uuid=session_record.id,
        name=prof.name if prof else "Visitor",
        phone_number=prof.phone_number if prof else "",
        gender=prof.gender if prof else "MALE",
        age=prof.age if prof else 30,
        persons_count=session_record.persons_count,
        temple_id=session_record.temple_id,
        village_id=prof.village_id if prof else None,
        village_name_custom=prof.village_name_custom if prof else None,
        purpose_id=session_record.purpose_id,
        visitor_date=session_record.visit_date,
        visitor_time=session_record.check_in_time,
        volunteer_id=session_record.volunteer_id,
        notes=session_record.notes,
        latitude=session_record.latitude,
        longitude=session_record.longitude,
        sync_status=session_record.sync_status,
        status=session_record.status,
        is_auto_closed=session_record.is_auto_closed,
        check_in_time=str(session_record.check_in_time),
        check_out_time=str(session_record.check_out_time) if session_record.check_out_time else None,
        duration=session_record.duration,
        created_at=session_record.created_at,
        updated_at=session_record.updated_at,
        purpose=purpose_resp,
        village=village_resp,
    )


@router.get("/", response_model=VisitorListResponse, responses={500: {"description": "Internal Server Error"}})
async def list_visitors(
    service: Annotated[VisitorService, Depends(get_visitor_service)],
    current_user: Annotated[User, Depends(get_current_user)],
    search: Optional[str] = None,
    purpose_id: Optional[str] = None,
    village_id: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    volunteer_id: Optional[str] = None,
    status_filter: Annotated[Optional[str], Query(alias="status")] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    """
    List Visit Sessions with filtering by Date Range, Status (INSIDE, CHECKED_OUT, AUTO_CLOSED), Purpose, Volunteer, and Search.
    """
    try:
        items, total, pages = await service.list_sessions(
            search=search,
            purpose_id=purpose_id,
            village_id=village_id,
            date_from=date_from,
            date_to=date_to,
            volunteer_id=volunteer_id,
            status_filter=status_filter,
            page=page,
            limit=limit,
        )
        dtos = [_map_session_to_visitor_response(s) for s in items]
        return VisitorListResponse(items=dtos, total=total, page=page, limit=limit, pages=pages).model_dump(mode="json")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"List visitors error: {str(e)}")


@router.get("/ledgers", response_model=DailyLedgerListResponse)
async def list_daily_ledgers(
    service: Annotated[VisitorService, Depends(get_visitor_service)],
    current_user: Annotated[User, Depends(get_current_user)],
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    search: Optional[str] = None,
    status_filter: Annotated[Optional[str], Query(alias="status")] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    """
    Daily Visit Ledger Endpoint:
    Returns ledgers list containing { date, summary, sessions } for each operational day.
    """
    ledger_data = await service.get_daily_ledgers_list(
        date_from=date_from,
        date_to=date_to,
        search=search,
        status_filter=status_filter,
        limit=limit,
    )

    items = []
    for item in ledger_data["items"]:
        mapped_sessions = [_map_session_to_visitor_response(s) for s in item["sessions"]]
        summary = DailyLedgerSummary(**item["summary"])
        items.append(DailyLedgerResponse(date=item["date"], summary=summary, sessions=mapped_sessions))

    today_ledger = None
    if ledger_data.get("today_ledger"):
        tl = ledger_data["today_ledger"]
        mapped_today_sessions = [_map_session_to_visitor_response(s) for s in tl["sessions"]]
        today_ledger = DailyLedgerResponse(
            date=tl["date"],
            summary=DailyLedgerSummary(**tl["summary"]),
            sessions=mapped_today_sessions,
        )

    return DailyLedgerListResponse(
        items=items,
        total_ledgers=ledger_data["total_ledgers"],
        today_ledger=today_ledger,
    )


@router.get("/ledgers/today", response_model=DailyLedgerResponse)
async def get_today_ledger(
    service: Annotated[VisitorService, Depends(get_visitor_service)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Today's Daily Visit Ledger:
    Loads ONLY today's operational ledger { date, summary, sessions }.
    If new calendar day, automatically returns fresh ledger with zero counts if empty.
    """
    data = await service.get_daily_ledger(date.today())
    mapped_sessions = [_map_session_to_visitor_response(s) for s in data["sessions"]]
    return DailyLedgerResponse(
        date=data["date"],
        summary=DailyLedgerSummary(**data["summary"]),
        sessions=mapped_sessions,
    )


@router.get("/ledgers/{visit_date}", response_model=DailyLedgerResponse)
async def get_daily_ledger_by_date(
    visit_date: date,
    service: Annotated[VisitorService, Depends(get_visitor_service)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Get Daily Visit Ledger by specific date { date, summary, sessions }.
    Past days are read-only (`summary.is_read_only = True`).
    """
    data = await service.get_daily_ledger(visit_date)
    mapped_sessions = [_map_session_to_visitor_response(s) for s in data["sessions"]]
    return DailyLedgerResponse(
        date=data["date"],
        summary=DailyLedgerSummary(**data["summary"]),
        sessions=mapped_sessions,
    )


@router.get("/check-duplicate")
async def check_duplicate(
    name: str,
    phone_number: str,
    visitor_date: date,
    service: Annotated[VisitorService, Depends(get_visitor_service)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    duplicate = await service.visitor_repo.check_duplicate(name=name, phone_number=phone_number, visitor_date=visitor_date)
    return {"is_duplicate": duplicate is not None, "existing_record": duplicate}


@router.post("/bulk-delete", status_code=status.HTTP_200_OK)
async def bulk_delete_visitors(
    payload: BulkDeleteRequest,
    service: Annotated[VisitorService, Depends(get_visitor_service)],
    current_user: Annotated[User, Depends(require_permission("visitors:delete"))],
):
    deleted_count = 0
    for v_id in payload.visitor_ids:
        try:
            await service.delete_session(v_id, current_user)
            deleted_count += 1
        except Exception:
            pass
    return {"message": f"Successfully deleted {deleted_count} visitor session records.", "deleted_count": deleted_count}


@router.get("/{visitor_id}", response_model=VisitorResponse)
async def get_visitor(
    visitor_id: str,
    service: Annotated[VisitorService, Depends(get_visitor_service)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    session_record = await service.get_session_by_id(visitor_id)
    return _map_session_to_visitor_response(session_record)


@router.put("/{visitor_id}", response_model=VisitorResponse)
async def update_visitor(
    visitor_id: str,
    payload: VisitorUpdate,
    service: Annotated[VisitorService, Depends(get_visitor_service)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    session_record = await service.update_visitor(visitor_id, payload, current_user)
    return _map_session_to_visitor_response(session_record)


@router.delete("/{visitor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_visitor(
    visitor_id: str,
    service: Annotated[VisitorService, Depends(get_visitor_service)],
    current_user: Annotated[User, Depends(require_permission("visitors:delete"))],
):
    await service.delete_session(visitor_id, current_user)


@router.put("/{visitor_id}/checkout", response_model=VisitorResponse, responses={500: {"description": "Internal Server Error"}})
@router.post("/{visitor_id}/checkout", response_model=VisitorResponse, responses={500: {"description": "Internal Server Error"}})
async def checkout_visitor(
    visitor_id: str,
    service: Annotated[VisitorService, Depends(get_visitor_service)],
    current_user: Annotated[User, Depends(get_current_user)],
    payload: Annotated[Optional[VisitorCheckoutRequest], Body()] = None,
):
    try:
        c_time = payload.checkout_time if payload else None
        dur = payload.duration if payload else None
        session_record = await service.checkout_visitor(visitor_id, checkout_time=c_time, duration=dur, current_user=current_user)
        return _map_session_to_visitor_response(session_record)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Checkout error: {str(e)}")
