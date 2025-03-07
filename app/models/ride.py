from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean, ARRAY, Index
from sqlalchemy.orm import relationship
from sqlalchemy import DateTime
import datetime

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


class Ride(Base):
    __tablename__ = "rides"

    id = Column(Integer, primary_key=True, index=True)
    driver_id = Column(Integer, ForeignKey("drivers.id"))
    car_id = Column(Integer, ForeignKey("cars.id"), nullable=True)  # Link to the car used for this ride
    start_location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    end_location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    price = Column(Float, nullable=False)
    recommended_price = Column(Float, nullable=False)
    max_riders = Column(Integer, default=4)
    current_riders = Column(Integer, default=0)
    ride_date = Column(DateTime, nullable=False)
    registration_open = Column(Boolean, default=True)
    distance_miles = Column(Float, nullable=False)
    estimated_duration_minutes = Column(Integer, nullable=False)  # Estimated travel time in minutes
    is_recurring = Column(Boolean, default=False)
    has_stops = Column(Boolean, default=False)  # Whether the ride has intermediate stops

    # Add relationships
    driver = relationship("Driver", back_populates="rides_as_driver")
    car = relationship("Car", back_populates="rides")
    start_location = relationship("Location", foreign_keys=[start_location_id])
    end_location = relationship("Location", foreign_keys=[end_location_id])
    riders = relationship("Customer", secondary="ride_riders")
    recurring_pattern = relationship("RecurringPattern", backref="ride")
    stops = relationship("RideStop", back_populates="ride", order_by="RideStop.stop_order")


class RideRiders(Base):
    __tablename__ = "ride_riders"

    ride_id = Column(Integer, ForeignKey("rides.id"), primary_key=True)
    rider_id = Column(Integer, ForeignKey("customers.id"), primary_key=True)
    payment_status = Column(Boolean, default=False)
    
    # Relationships
    ride = relationship("Ride", backref="ride_riders")
    rider = relationship("Customer", back_populates="rides_as_passenger")
