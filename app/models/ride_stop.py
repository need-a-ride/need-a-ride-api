from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.database.session import Base

class RideStop(Base):
    __tablename__ = "ride_stops"

    id = Column(Integer, primary_key=True, index=True)
    ride_id = Column(Integer, ForeignKey("rides.id"), nullable=False)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    stop_order = Column(Integer, nullable=False)  # Order of the stop in the ride
    
    # Relationships
    ride = relationship("Ride", back_populates="stops")
    location = relationship("Location", back_populates="ride_stops") 
