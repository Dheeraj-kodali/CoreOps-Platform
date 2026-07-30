from sqlalchemy import Column, String, Boolean, Text
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Temple(BaseModel):
    __tablename__ = "temples"

    name = Column(String(200), nullable=False, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    address = Column(Text, nullable=True)
    contact_phone = Column(String(20), nullable=True)
    contact_email = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    volunteers = relationship("Volunteer", back_populates="temple")
    visitors = relationship("Visitor", back_populates="temple")
    purposes = relationship("Purpose", back_populates="temple")
    settings = relationship("Setting", back_populates="temple")
