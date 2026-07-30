from sqlalchemy import Column, Integer, String, Text, Date, Time, ForeignKey
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
    
    sync_status = Column(String(20), default="SYNCED", nullable=False)  # PENDING, SYNCED, CONFLICT

    temple = relationship("Temple", back_populates="visitors")
    village = relationship("Village", back_populates="visitors")
    purpose = relationship("Purpose", back_populates="visitors")
    volunteer = relationship("User", back_populates="visitors_registered")
    notifications = relationship("Notification", back_populates="visitor")
