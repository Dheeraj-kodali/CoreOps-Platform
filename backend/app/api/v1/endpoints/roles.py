from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.api.deps import get_current_user, require_permission
from app.models.user import User, Role, Permission
from app.schemas.user import RoleCreate, RoleResponse

router = APIRouter()

ROLE_NOT_FOUND = "Role not found"
PERM_ROLES_MANAGE = "roles:manage"


@router.get("/", response_model=List[RoleResponse])
async def list_roles(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    stmt = select(Role).options(selectinload(Role.permissions)).filter(Role.is_deleted.is_(False))
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
    payload: RoleCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission(PERM_ROLES_MANAGE))],
):
    stmt = select(Role).filter(Role.name == payload.name, Role.is_deleted.is_(False))
    res = await db.execute(stmt)
    if res.scalars().first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Role name already exists")

    role = Role(name=payload.name, description=payload.description)
    if payload.permission_ids:
        perm_stmt = select(Permission).filter(Permission.id.in_(payload.permission_ids))
        perms_res = await db.execute(perm_stmt)
        role.permissions = list(perms_res.scalars().all())

    db.add(role)
    await db.commit()

    full_role_stmt = select(Role).options(selectinload(Role.permissions)).filter(Role.id == role.id)
    r_res = await db.execute(full_role_stmt)
    return r_res.scalars().first()


@router.get("/{role_id}", response_model=RoleResponse)
async def get_role(
    role_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    stmt = select(Role).options(selectinload(Role.permissions)).filter(Role.id == role_id, not Role.is_deleted)
    res = await db.execute(stmt)
    role = res.scalars().first()
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ROLE_NOT_FOUND)
    return role


@router.put("/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: str,
    payload: RoleCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission(PERM_ROLES_MANAGE))],
):
    stmt = select(Role).options(selectinload(Role.permissions)).filter(Role.id == role_id, not Role.is_deleted)
    res = await db.execute(stmt)
    role = res.scalars().first()
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ROLE_NOT_FOUND)

    role.name = payload.name
    role.description = payload.description
    if payload.permission_ids is not None:
        perm_stmt = select(Permission).filter(Permission.id.in_(payload.permission_ids))
        perms_res = await db.execute(perm_stmt)
        role.permissions = list(perms_res.scalars().all())

    db.add(role)
    await db.commit()
    await db.refresh(role)
    return role


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(
    role_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission(PERM_ROLES_MANAGE))],
):
    stmt = select(Role).filter(Role.id == role_id, not Role.is_deleted)
    res = await db.execute(stmt)
    role = res.scalars().first()
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ROLE_NOT_FOUND)

    role.is_deleted = True
    db.add(role)
    await db.commit()
