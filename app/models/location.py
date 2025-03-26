from sqlalchemy import Column, Integer, String, Float, DateTime, Index
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database.session import Base

class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    address = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    formatted_address = Column(String, nullable=True)
    last_verified = Column(DateTime, default=datetime.utcnow)
    
    # Add index for faster geospatial queries
    __table_args__ = (Index("idx_lat_long", "latitude", "longitude"),)
    
    # Relationships
    rides_as_start = relationship("Ride", foreign_keys="Ride.start_location_id", back_populates="start_location_obj")
    rides_as_end = relationship("Ride", foreign_keys="Ride.end_location_id", back_populates="end_location_obj")
    ride_stops = relationship("RideStop", back_populates="location") 
