from typing import List, Optional
from pydantic import BaseModel


class V2TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class V2RefreshTokenRequest(BaseModel):
    refresh_token: str


class V2RefreshTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class V2LoginRequest(BaseModel):
    username: str
    password: str


class V2UserProfileResponse(BaseModel):
    id: str
    username: str
    email: Optional[str] = None
    full_name: str
    phone_number: Optional[str] = None
    temple_id: str
    is_active: bool
    roles: List[str]
    permissions: List[str]
