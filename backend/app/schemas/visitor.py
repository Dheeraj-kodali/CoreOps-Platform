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
    id_proof_url: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    status: Optional[str] = "INSIDE"
    is_auto_closed: Optional[bool] = False
    check_in_time: Optional[str] = None
    check_out_time: Optional[str] = None
    duration: Optional[str] = None


class VisitorCreate(VisitorBase):
    visitor_uuid: str = Field(..., min_length=36, max_length=36)


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

    @model_validator(mode="before")
    @classmethod
    def populate_lifecycle_fields(cls, data: Any) -> Any:
        try:
            if isinstance(data, dict):
                from app.services.visitor_lifecycle import eval_visitor_lifecycle
                info = eval_visitor_lifecycle(data)
                data["status"] = info["status"]
                data["is_auto_closed"] = info["is_auto_closed"]
                data["check_in_time"] = info["check_in_time"]
                data["check_out_time"] = info["check_out_time"]
                data["duration"] = info["duration"]
        except Exception:
            pass
        return data

    model_config = ConfigDict(from_attributes=True)


class VisitorListResponse(BaseModel):
    items: List[VisitorResponse]
    total: int
    page: int
    limit: int
    pages: int
