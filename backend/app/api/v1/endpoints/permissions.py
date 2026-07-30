from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.api.deps import get_current_user, require_permission
from app.models.user import User, Permission
from app.schemas.user import PermissionCreate, PermissionResponse

router = APIRouter()


@router.get("/", response_model=List[PermissionResponse])
async def list_permissions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = select(Permission).filter(Permission.is_deleted.is_(False))
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/", response_model=PermissionResponse, status_code=status.HTTP_201_CREATED)
async def create_permission(
    payload: PermissionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("roles:manage")),
):
    stmt = select(Permission).filter(Permission.code == payload.code, Permission.is_deleted.is_(False))
    res = await db.execute(stmt)
    if res.scalars().first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Permission code already exists")

    perm = Permission(code=payload.code, module=payload.module, description=payload.description)
    db.add(perm)
    await db.commit()
    await db.refresh(perm)
    return perm


@router.delete("/{permission_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_permission(
    permission_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("roles:manage")),
):
    stmt = select(Permission).filter(Permission.id == permission_id, not Permission.is_deleted)
    res = await db.execute(stmt)
    perm = res.scalars().first()
    if not perm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found")

    perm.is_deleted = True
    db.add(perm)
    await db.commit()
