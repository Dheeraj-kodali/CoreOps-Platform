from typing import Annotated, List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.core.security import get_password_hash, validate_password_policy
from app.api.deps import get_current_user, require_permission
from app.models.user import User, Role
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate, UserResponse

router = APIRouter()

USER_NOT_FOUND = "User not found"
PERM_USERS_MANAGE = "users:manage"


class RoleAssignmentRequest(BaseModel):
    role_ids: List[str]


@router.get("/", response_model=List[UserResponse])
async def list_users(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission("users:read"))],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
    role_name: Optional[str] = None,
):
    stmt = (
        select(User)
        .options(selectinload(User.roles).selectinload(Role.permissions))
        .filter(User.is_deleted.is_(False))
    )
    if role_name:
        stmt = stmt.join(User.roles).filter(Role.name == role_name)

    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission("users:create"))],
):
    user_repo = UserRepository(db)
    existing_username = await user_repo.get_by_username(payload.username)
    if existing_username:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists")

    if payload.email:
        existing_email = await user_repo.get_by_email(payload.email)
        if existing_email:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")

    valid_pw, msg = validate_password_policy(payload.password)
    if not valid_pw:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)

    hashed_pw = get_password_hash(payload.password)
    user_data = payload.model_dump(exclude={"role_ids"})
    user_data["password_hash"] = hashed_pw

    user = await user_repo.create(user_data, user_id=current_user.id)

    if payload.role_ids:
        await user_repo.assign_roles(user.id, payload.role_ids)
        await db.commit()

    return await user_repo.get_by_id_with_relations(user.id)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id_with_relations(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=USER_NOT_FOUND)
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    payload: UserUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission(PERM_USERS_MANAGE))],
):
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id_with_relations(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=USER_NOT_FOUND)

    update_dict = payload.model_dump(exclude_unset=True, exclude={"role_ids", "password"})
    if payload.password:
        valid_pw, msg = validate_password_policy(payload.password)
        if not valid_pw:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)
        update_dict["password_hash"] = get_password_hash(payload.password)

    await user_repo.update(user, update_dict, user_id=current_user.id)

    if payload.role_ids is not None:
        await user_repo.assign_roles(user.id, payload.role_ids)

    await db.commit()
    return await user_repo.get_by_id_with_relations(user.id)


@router.put("/{user_id}/role", response_model=UserResponse)
async def assign_user_role(
    user_id: str,
    payload: RoleAssignmentRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission(PERM_USERS_MANAGE))],
):
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id_with_relations(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=USER_NOT_FOUND)

    await user_repo.assign_roles(user.id, payload.role_ids)
    await db.commit()
    return await user_repo.get_by_id_with_relations(user.id)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission(PERM_USERS_MANAGE))],
):
    user_repo = UserRepository(db)
    success = await user_repo.soft_delete(user_id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=USER_NOT_FOUND)
    await db.commit()
