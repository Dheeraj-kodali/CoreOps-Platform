from datetime import datetime, date, time
from sqlalchemy import Column, Integer, String, Text, Date, Time, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class VisitSession(BaseModel):
    __tablename__ = "visit_sessions"

    visitor_profile_id = Column(String(36), ForeignKey("visitor_profiles.id"), nullable=False, index=True)
    temple_id = Column(String(36), ForeignKey("temples.id"), nullable=True, index=True)
    
    visit_date = Column(Date, nullable=False, index=True)
    check_in_time = Column(Time, nullable=False)
    check_out_time = Column(Time, nullable=True)
    
    persons_count = Column(Integer, default=1, nullable=False)
    purpose_id = Column(String(36), ForeignKey("purposes.id"), nullable=False, index=True)
    notes = Column(Text, nullable=True)
    
    volunteer_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    status = Column(String(20), default="INSIDE", nullable=False, index=True)  # INSIDE, CHECKED_OUT, AUTO_CLOSED
    sync_status = Column(String(20), default="SYNCED", nullable=False)  # PENDING, SYNCED, CONFLICT

    visitor_profile = relationship("VisitorProfile", back_populates="visit_sessions")
    temple = relationship("Temple")
    purpose = relationship("Purpose")
    volunteer = relationship("User")

    @property
    def is_auto_closed(self) -> bool:
        return self.status == "AUTO_CLOSED"

    @property
    def duration(self) -> str:
        if not self.check_in_time:
            return "N/A"
        
        in_datetime = datetime.combine(self.visit_date or date.today(), self.check_in_time)
        if self.check_out_time:
            out_datetime = datetime.combine(self.visit_date or date.today(), self.check_out_time)
        else:
            if self.status == "AUTO_CLOSED":
                out_datetime = datetime.combine(self.visit_date or date.today(), time(23, 59, 59))
            else:
                out_datetime = datetime.now()
        
        diff = out_datetime - in_datetime
        mins = max(1, int(diff.total_seconds() / 60))
        if mins < 60:
            return f"{mins} min"
        hours = mins // 60
        rem_mins = mins % 60
        return f"{hours} hr {rem_mins:02d} min"
