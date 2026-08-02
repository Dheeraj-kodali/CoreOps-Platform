from datetime import date, time, datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field, ConfigDict, model_validator


class PurposeResponse(BaseModel):
    id: str
    name_en: str
    name_te: str
    code: str

    model_config = ConfigDict(from_attributes=True)


class VillageResponse(BaseModel):
    id: str
    name_en: str
    name_te: str
    district: Optional[str] = None
    state: str

    model_config = ConfigDict(from_attributes=True)


# --- VISITOR PROFILE SCHEMAS ---

class VisitorProfileBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    phone_number: str = Field(..., min_length=5, max_length=20)
    village_id: Optional[str] = None
    village_name_custom: Optional[str] = None
    gender: str = Field(default="MALE")
    age: int = Field(default=30)
    default_purpose_id: Optional[str] = None


class VisitorProfileCreate(VisitorProfileBase):
    visitor_id: Optional[str] = None


class VisitorProfileUpdate(BaseModel):
    name: Optional[str] = None
    phone_number: Optional[str] = None
    village_id: Optional[str] = None
    village_name_custom: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    default_purpose_id: Optional[str] = None


class VisitorProfileResponse(VisitorProfileBase):
    id: str
    visitor_id: str
    created_at: datetime
    updated_at: datetime
    village: Optional[VillageResponse] = None
    default_purpose: Optional[PurposeResponse] = None

    model_config = ConfigDict(from_attributes=True)


# --- VISIT SESSION SCHEMAS ---

class VisitSessionBase(BaseModel):
    persons_count: int = Field(default=1, ge=1)
    purpose_id: str
    notes: Optional[str] = None
    visit_date: date
    check_in_time: time
    check_out_time: Optional[time] = None
    temple_id: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class VisitSessionCreate(BaseModel):
    visitor_uuid: Optional[str] = None
    # Can contain either profile_id OR visitor profile info for new visitors
    visitor_profile_id: Optional[str] = None
    name: Optional[str] = None
    phone_number: str
    gender: Optional[str] = "MALE"
    age: Optional[int] = 30
    village_id: Optional[str] = None
    village_name_custom: Optional[str] = None
    purpose_id: Optional[str] = None
    persons_count: int = 1
    visitor_date: date
    visitor_time: time
    notes: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class VisitSessionResponse(BaseModel):
    id: str
    visitor_profile_id: str
    visit_date: date
    check_in_time: str
    check_out_time: Optional[str] = None
    duration: Optional[str] = None
    persons_count: int
    purpose_id: str
    notes: Optional[str] = None
    volunteer_id: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    status: str = "INSIDE"
    is_auto_closed: bool = False
    sync_status: str = "SYNCED"
    created_at: datetime
    updated_at: datetime

    visitor_profile: Optional[VisitorProfileResponse] = None
    purpose: Optional[PurposeResponse] = None

    model_config = ConfigDict(from_attributes=True)


# --- PHONE LOOKUP RESPONSE ---

class LastVisitSummary(BaseModel):
    last_visit_date: Optional[str] = None
    last_visit_time: Optional[str] = None
    last_purpose: Optional[str] = None
    total_visits: int = 0
    status: Optional[str] = None


class PhoneLookupResponse(BaseModel):
    profile_exists: bool
    profile: Optional[VisitorProfileResponse] = None
    last_visit: Optional[LastVisitSummary] = None


# --- COMPATIBILITY DTOs FOR EXISTING FRONTEND & APK ---

class VisitorBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    phone_number: str
    gender: Optional[str] = "MALE"
    age: Optional[int] = 30
    persons_count: Optional[int] = 1
    temple_id: Optional[str] = None
    village_id: Optional[str] = None
    village_name_custom: Optional[str] = None
    purpose_id: Optional[str] = None
    temple_service: Optional[str] = None
    visitor_date: date
    visitor_time: time
    notes: Optional[str] = None
    photo_url: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class VisitorCreate(VisitorBase):
    visitor_uuid: Optional[str] = None


class VisitorUpdate(BaseModel):
    name: Optional[str] = None
    phone_number: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    persons_count: Optional[int] = None
    village_id: Optional[str] = None
    village_name_custom: Optional[str] = None
    purpose_id: Optional[str] = None
    temple_service: Optional[str] = None
    visitor_date: Optional[date] = None
    visitor_time: Optional[time] = None
    notes: Optional[str] = None
    photo_url: Optional[str] = None
    id_proof_url: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class VisitorResponse(VisitorBase):
    id: str
    visitor_uuid: str
    volunteer_id: str
    sync_status: str
    status: str = "INSIDE"
    is_auto_closed: bool = False
    check_in_time: Optional[str] = None
    check_out_time: Optional[str] = None
    duration: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    purpose: Optional[PurposeResponse] = None
    village: Optional[VillageResponse] = None

    model_config = ConfigDict(from_attributes=True)


class VisitorListResponse(BaseModel):
    items: List[VisitorResponse]
    total: int
    page: int = 1
    pages: int = 1
    limit: int = 50


# --- DAILY VISIT LEDGER SCHEMAS ---

class DailyLedgerSummary(BaseModel):
    date: str
    display_date: str
    total_visitors: int = 0
    people_inside: int = 0
    checked_out: int = 0
    auto_closed: int = 0
    purpose_breakdown: dict = Field(default_factory=dict)
    volunteer_breakdown: dict = Field(default_factory=dict)
    avg_stay_minutes: str = "42 min"
    peak_hour: str = "09:00 AM - 11:30 AM"
    is_read_only: bool = False


class DailyLedgerResponse(BaseModel):
    date: str
    summary: DailyLedgerSummary
    sessions: List[VisitorResponse]


class DailyLedgerListResponse(BaseModel):
    items: List[DailyLedgerResponse]
    total_ledgers: int
    today_ledger: Optional[DailyLedgerResponse] = None
