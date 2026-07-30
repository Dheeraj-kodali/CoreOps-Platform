from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Setting(BaseModel):
    __tablename__ = "settings"

    temple_id = Column(String(36), ForeignKey("temples.id"), nullable=True, index=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    value_json = Column(Text, nullable=False)
    description = Column(Text, nullable=True)

    temple = relationship("Temple", back_populates="settings")


# Alias for system_settings specification
SystemSetting = Setting
