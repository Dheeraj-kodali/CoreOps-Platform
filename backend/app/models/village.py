from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Village(BaseModel):
    __tablename__ = "villages"

    name_en = Column(String(100), nullable=False, index=True)
    name_te = Column(String(100), nullable=False, index=True)
    district = Column(String(100), nullable=True)
    state = Column(String(100), default="Andhra Pradesh", nullable=False)
    pin_code = Column(String(10), nullable=True)

    visitors = relationship("Visitor", back_populates="village")
