from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Purpose(BaseModel):
    __tablename__ = "purposes"

    temple_id = Column(String(36), ForeignKey("temples.id"), nullable=True, index=True)
    name_en = Column(String(100), nullable=False)
    name_te = Column(String(100), nullable=False)
    code = Column(String(50), unique=True, nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)

    temple = relationship("Temple", back_populates="purposes")
    visitors = relationship("Visitor", back_populates="purpose")
