from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database.session import Base

class RecurringPattern(Base):
    __tablename__ = "recurring_patterns"

    id = Column(Integer, primary_key=True, index=True)
    days_of_week = Column(String)  # Stored as comma-separated days (1-7)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    ride_id = Column(Integer, ForeignKey("rides.id"))
    
    # Relationship
    ride = relationship("Ride", back_populates="recurring_pattern_obj") 
