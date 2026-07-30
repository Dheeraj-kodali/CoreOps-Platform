from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Volunteer(BaseModel):
    __tablename__ = "volunteers"

    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    temple_id = Column(String(36), ForeignKey("temples.id"), nullable=False, index=True)
    badge_number = Column(String(50), nullable=True, index=True)
    status = Column(String(20), default="ACTIVE", nullable=False)  # ACTIVE, INACTIVE, SUSPENDED

    user = relationship("User", back_populates="volunteers")
    temple = relationship("Temple", back_populates="volunteers")
