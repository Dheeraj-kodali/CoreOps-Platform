from sqlalchemy import Column, Integer, String, Text, Date, Time, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Visitor(BaseModel):
    __tablename__ = "visitors"

    visitor_uuid = Column(String(36), unique=True, nullable=False, index=True)
    name = Column(String(150), nullable=False, index=True)
    phone_number = Column(String(20), nullable=False, index=True)
    gender = Column(String(10), nullable=False)  # MALE, FEMALE, OTHER
    age = Column(Integer, nullable=False)
    persons_count = Column(Integer, default=1, nullable=False)
    
    temple_id = Column(String(36), ForeignKey("temples.id"), nullable=True, index=True)
    village_id = Column(String(36), ForeignKey("villages.id"), nullable=True, index=True)
    village_name_custom = Column(String(150), nullable=True)
    
    purpose_id = Column(String(36), ForeignKey("purposes.id"), nullable=False, index=True)
    temple_service = Column(String(150), nullable=True)
    
    visitor_date = Column(Date, nullable=False, index=True)
    visitor_time = Column(Time, nullable=False)
    
    volunteer_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    notes = Column(Text, nullable=True)
    photo_url = Column(String(500), nullable=True)
    id_proof_url = Column(String(500), nullable=True)
    
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    sync_status = Column(String(20), default="SYNCED", nullable=False)  # PENDING, SYNCED, CONFLICT

    temple = relationship("Temple", back_populates="visitors")
    village = relationship("Village", back_populates="visitors")
    purpose = relationship("Purpose", back_populates="visitors")
    volunteer = relationship("User", back_populates="visitors_registered")
    notifications = relationship("Notification", back_populates="visitor")

    @property
    def status(self) -> str:
        from app.services.visitor_lifecycle import eval_visitor_lifecycle
        return eval_visitor_lifecycle(self)["status"]

    @property
    def is_auto_closed(self) -> bool:
        from app.services.visitor_lifecycle import eval_visitor_lifecycle
        return eval_visitor_lifecycle(self)["is_auto_closed"]

    @property
    def check_in_time(self) -> str:
        from app.services.visitor_lifecycle import eval_visitor_lifecycle
        return eval_visitor_lifecycle(self)["check_in_time"]

    @property
    def check_out_time(self) -> str:
        from app.services.visitor_lifecycle import eval_visitor_lifecycle
        return eval_visitor_lifecycle(self)["check_out_time"]

    @property
    def duration(self) -> str:
        from app.services.visitor_lifecycle import eval_visitor_lifecycle
        return eval_visitor_lifecycle(self)["duration"]
