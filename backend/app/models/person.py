from sqlalchemy import Column, String, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Person(BaseModel):
    __tablename__ = "persons"

    temple_id = Column(String(36), ForeignKey("temples.id"), nullable=True, index=True)
    name = Column(String(150), nullable=False, index=True)
    phone = Column(String(20), unique=True, nullable=False, index=True)
    village = Column(String(100), nullable=False, index=True)
    address = Column(Text, nullable=True)
    first_visit = Column(String(50), nullable=False)
    last_visit = Column(String(50), nullable=False)
    total_visits = Column(Integer, default=1, nullable=False)

    temple = relationship("Temple", backref="persons")

    @property
    def mobile_number(self) -> str:
        return self.phone
