from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class VisitorProfile(BaseModel):
    __tablename__ = "visitor_profiles"

    visitor_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(150), nullable=False, index=True)
    phone_number = Column(String(20), unique=True, nullable=False, index=True)
    
    village_id = Column(String(36), ForeignKey("villages.id"), nullable=True, index=True)
    village_name_custom = Column(String(150), nullable=True)
    
    gender = Column(String(10), nullable=False, default="MALE")  # MALE, FEMALE, OTHER
    age = Column(Integer, nullable=False, default=30)
    
    default_purpose_id = Column(String(36), ForeignKey("purposes.id"), nullable=True, index=True)

    village = relationship("Village")
    default_purpose = relationship("Purpose")
    visit_sessions = relationship("VisitSession", back_populates="visitor_profile", cascade="all, delete-orphan")
