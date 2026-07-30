from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr, ConfigDict


class PermissionResponse(BaseModel):
    id: str
    code: str
    module: str
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class PermissionCreate(BaseModel):
    code: str = Field(..., min_length=3, max_length=100)
    module: str = Field(..., min_length=2, max_length=50)
    description: Optional[str] = None


class RoleResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    permissions: List[PermissionResponse] = []

    model_config = ConfigDict(from_attributes=True)


class RoleCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    description: Optional[str] = None
    permission_ids: List[str] = []


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    full_name: str = Field(..., min_length=2, max_length=100)
    phone_number: Optional[str] = Field(None, pattern=r"^\+?[0-9]{10,15}$")
    is_active: bool = True


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    role_ids: List[str] = []


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None
    role_ids: Optional[List[str]] = None


class UserResponse(UserBase):
    id: str
    roles: List[RoleResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LoginRequest(BaseModel):
    username: str
    password: str
