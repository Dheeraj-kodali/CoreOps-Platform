from datetime import date
from typing import Optional, List
from pydantic import BaseModel
from fastapi import APIRouter, Depends, Query, status
from app.api.deps import get_current_user, require_permission, get_visitor_service
from app.models.user import User
from app.services.visitor_service import VisitorService
from app.schemas.visitor import VisitorCreate, VisitorUpdate, VisitorResponse, VisitorListResponse

router = APIRouter()


class BulkDeleteRequest(BaseModel):
    visitor_ids: List[str]


@router.post("/", response_model=VisitorResponse, status_code=status.HTTP_201_CREATED)
async def create_visitor(
    payload: VisitorCreate,
    service: VisitorService = Depends(get_visitor_service),
    current_user: User = Depends(get_current_user),
):
    return await service.register_visitor(payload, current_user)


@router.get("/", response_model=VisitorListResponse)
async def list_visitors(
    search: Optional[str] = None,
    purpose_id: Optional[str] = None,
    village_id: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    volunteer_id: Optional[str] = None,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    service: VisitorService = Depends(get_visitor_service),
    current_user: User = Depends(get_current_user),
):
    items, total, pages = await service.list_visitors(
        search=search,
        purpose_id=purpose_id,
        village_id=village_id,
        date_from=date_from,
        date_to=date_to,
        volunteer_id=volunteer_id,
        page=page,
        limit=limit,
    )
    return VisitorListResponse(items=items, total=total, page=page, limit=limit, pages=pages)


@router.get("/check-duplicate")
async def check_duplicate(
    name: str,
    phone_number: str,
    visitor_date: date,
    service: VisitorService = Depends(get_visitor_service),
    current_user: User = Depends(get_current_user),
):
    duplicate = await service.check_duplicate(name=name, phone_number=phone_number, visitor_date=visitor_date)
    return {"is_duplicate": duplicate is not None, "existing_record": duplicate}


@router.post("/bulk-delete", status_code=status.HTTP_200_OK)
async def bulk_delete_visitors(
    payload: BulkDeleteRequest,
    service: VisitorService = Depends(get_visitor_service),
    current_user: User = Depends(require_permission("visitors:delete")),
):
    deleted_count = 0
    for v_id in payload.visitor_ids:
        try:
            await service.delete_visitor(v_id, current_user)
            deleted_count += 1
        except Exception:
            pass
    return {"message": f"Successfully deleted {deleted_count} visitor records.", "deleted_count": deleted_count}


@router.get("/{visitor_id}", response_model=VisitorResponse)
async def get_visitor(
    visitor_id: str,
    service: VisitorService = Depends(get_visitor_service),
    current_user: User = Depends(get_current_user),
):
    return await service.get_visitor_by_id(visitor_id)


@router.put("/{visitor_id}", response_model=VisitorResponse)
async def update_visitor(
    visitor_id: str,
    payload: VisitorUpdate,
    service: VisitorService = Depends(get_visitor_service),
    current_user: User = Depends(get_current_user),
):
    return await service.update_visitor(visitor_id, payload, current_user)


@router.delete("/{visitor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_visitor(
    visitor_id: str,
    service: VisitorService = Depends(get_visitor_service),
    current_user: User = Depends(require_permission("visitors:delete")),
):
    await service.delete_visitor(visitor_id, current_user)
