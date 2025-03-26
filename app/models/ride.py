from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean, ARRAY, Index, Enum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy import DateTime
import datetime
import enum

from app.database.session import Base


class RecurringPattern(Base):
    __tablename__ = "recurring_patterns"

    id = Column(Integer, primary_key=True, index=True)
    days_of_week = Column(String)  # Stored as comma-separated days (1-7)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    ride_id = Column(Integer, ForeignKey("rides.id"))


class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    address = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    formatted_address = Column(String, nullable=True)
    last_verified = Column(DateTime, default=datetime.datetime.now(datetime.UTC))

    __table_args__ = (Index("idx_lat_long", "latitude", "longitude"),)


class RideStop(Base):
    __tablename__ = "ride_stops"

    id = Column(Integer, primary_key=True, index=True)
    ride_id = Column(Integer, ForeignKey("rides.id"), nullable=False)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    stop_order = Column(Integer, nullable=False)  # Order of the stop in the ride
    
    # Relationships
    ride = relationship("Ride", back_populates="stops")
    location = relationship("Location")


class RideStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class Ride(Base):
    __tablename__ = "rides"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Ride Details
    status = Column(Enum(RideStatus), default=RideStatus.PENDING)
    distance_miles = Column(Float)
    duration_minutes = Column(Integer)
    route_polyline = Column(String)
    route_steps = Column(String)  # JSON string of route steps
    
    # Pricing
    base_price = Column(Float)
    stop_fee = Column(Float)
    time_fee = Column(Float)
    platform_fee = Column(Float)
    stripe_fees = Column(Float)
    total_price = Column(Float)
    driver_earnings = Column(Float)
    
    # Scheduling
    scheduled_for = Column(DateTime, nullable=True)
    pickup_time = Column(DateTime, nullable=True)
    dropoff_time = Column(DateTime, nullable=True)
    
    # Additional Information
    number_of_stops = Column(Integer, default=0)
    is_recurring = Column(Boolean, default=False)
    notes = Column(String, nullable=True)
    
    # Safety and Verification
    emergency_contact = Column(String, nullable=True)  # JSON string of emergency contact
    verification_code = Column(String, nullable=True)
    
    # Foreign Keys
    driver_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    creator_id = Column(Integer, ForeignKey("users.id"))
    car_id = Column(Integer, ForeignKey("cars.id"), nullable=True)
    start_location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    end_location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    
    # Relationships
    driver = relationship("User", foreign_keys=[driver_id], back_populates="driven_rides")
    creator = relationship("User", foreign_keys=[creator_id], back_populates="created_rides")
    car = relationship("Car", back_populates="rides")
    start_location_obj = relationship("Location", foreign_keys=[start_location_id])
    end_location_obj = relationship("Location", foreign_keys=[end_location_id])
    riders = relationship("Customer", secondary="ride_riders")
    recurring_pattern_obj = relationship("RecurringPattern", backref="ride")
    stops = relationship("RideStop", back_populates="ride", order_by="RideStop.stop_order")


class RideRiders(Base):
    __tablename__ = "ride_riders"

    ride_id = Column(Integer, ForeignKey("rides.id"), primary_key=True)
    rider_id = Column(Integer, ForeignKey("customers.id"), primary_key=True)
    payment_status = Column(Boolean, default=False)
    
    # Relationships
    ride = relationship("Ride", backref="ride_riders")
    rider = relationship("Customer", back_populates="rides_as_passenger")
