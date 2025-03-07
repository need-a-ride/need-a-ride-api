from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Enum
from sqlalchemy.orm import relationship
from app.database.session import Base
import enum
import datetime


class UserType(str, enum.Enum):
    DRIVER = "driver"
    CUSTOMER = "customer"


class Driver(Base):
    __tablename__ = "drivers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    rating = Column(Float, default=0)
    is_verified = Column(Boolean, default=False)
    license_number = Column(String, nullable=True)
    license_expiry = Column(DateTime, nullable=True)
    # OAuth fields for future use
    google_id = Column(String, unique=True, nullable=True)
    profile_picture = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    # Relationships
    cars = relationship("Car", back_populates="driver", cascade="all, delete-orphan")
    rides_as_driver = relationship("Ride", back_populates="driver")


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    rating = Column(Float, default=0)
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.UTC))
    # OAuth fields for future use
    google_id = Column(String, unique=True, nullable=True)
    profile_picture = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    # Relationships
    rides_as_passenger = relationship("RideRiders", back_populates="rider")
