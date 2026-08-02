from datetime import date, time, datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


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


from pydantic import BaseModel, Field, ConfigDict, computed_field

class VisitorResponse(VisitorBase):
    id: str
    visitor_uuid: str
    volunteer_id: str
    sync_status: str
    created_at: datetime
    updated_at: datetime
    purpose: Optional[PurposeResponse] = None
    village: Optional[VillageResponse] = None

    @computed_field
    @property
    def status(self) -> str:
        from app.services.visitor_lifecycle import eval_visitor_lifecycle
        return eval_visitor_lifecycle(self)["status"]

    @computed_field
    @property
    def is_auto_closed(self) -> bool:
        from app.services.visitor_lifecycle import eval_visitor_lifecycle
        return eval_visitor_lifecycle(self)["is_auto_closed"]

    @computed_field
    @property
    def check_in_time(self) -> str:
        from app.services.visitor_lifecycle import eval_visitor_lifecycle
        return eval_visitor_lifecycle(self)["check_in_time"]

    @computed_field
    @property
    def check_out_time(self) -> Optional[str]:
        from app.services.visitor_lifecycle import eval_visitor_lifecycle
        return eval_visitor_lifecycle(self)["check_out_time"]

    @computed_field
    @property
    def duration(self) -> Optional[str]:
        from app.services.visitor_lifecycle import eval_visitor_lifecycle
        return eval_visitor_lifecycle(self)["duration"]

    model_config = ConfigDict(from_attributes=True)


class VisitorListResponse(BaseModel):
    items: List[VisitorResponse]
    total: int
    page: int
    limit: int
    pages: int
