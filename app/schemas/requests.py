from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum


class UserType(str, Enum):
    DRIVER = "driver"
    CUSTOMER = "customer"


class RefreshTokenRequest(BaseModel):
    """Request model for token refresh endpoint"""
    refresh_token: Optional[str] = None


# Auth Request Models
class UserLoginRequest(BaseModel):
    """Request model for login endpoint"""
    email: str = Field(..., description="User email")
    password: str = Field(..., description="User password")


class UserRegisterRequest(BaseModel):
    """Request model for user registration endpoint"""
    name: str = Field(..., description="User full name")
    email: str = Field(..., description="User email")
    phone: str = Field(..., description="User phone number")
    password: str = Field(..., description="User password")
    user_type: UserType = Field(..., description="Type of user (driver or customer)")
    
    # Driver-specific fields (optional, can be updated later)
    license_number: Optional[str] = Field(None, description="Driver's license number (optional, can be added later)")
    license_expiry: Optional[datetime] = Field(None, description="Driver's license expiry date (optional, can be added later)")


# Car Request Models
class CarCreateRequest(BaseModel):
    """Request model for creating a new car"""
    make: str = Field(..., description="Car manufacturer")
    model: str = Field(..., description="Car model")
    year: int = Field(..., description="Car year of manufacture")
    color: str = Field(..., description="Car color")
    license_plate: str = Field(..., description="Car license plate number")
    capacity: int = Field(4, description="Car passenger capacity")
    air_conditioned: bool = Field(False, description="Whether the car has air conditioning")
    has_wheelchair_access: bool = Field(False, description="Whether the car has wheelchair access")


class CarUpdateRequest(BaseModel):
    """Request model for updating a car"""
    make: Optional[str] = Field(None, description="Car manufacturer")
    model: Optional[str] = Field(None, description="Car model")
    year: Optional[int] = Field(None, description="Car year of manufacture")
    color: Optional[str] = Field(None, description="Car color")
    license_plate: Optional[str] = Field(None, description="Car license plate number")
    capacity: Optional[int] = Field(None, description="Car passenger capacity")
    air_conditioned: Optional[bool] = Field(None, description="Whether the car has air conditioning")
    has_wheelchair_access: Optional[bool] = Field(None, description="Whether the car has wheelchair access")
    is_active: Optional[bool] = Field(None, description="Whether the car is active")


# Ride Request Models
class RecurringPatternRequest(BaseModel):
    """Request model for recurring ride pattern"""
    days_of_week: List[int] = Field(..., description="Days of week (1-7 representing Monday-Sunday)")
    start_date: datetime = Field(..., description="Start date of recurring pattern")
    end_date: datetime = Field(..., description="End date of recurring pattern")


class CreateRideRequest(BaseModel):
    """Request model for creating a new ride"""
    car_id: int = Field(..., description="ID of the car to use for this ride")
    start_location: str = Field(..., description="Starting location address")
    end_location: str = Field(..., description="Destination address")
    start_coordinates: str = Field(..., description="Starting coordinates (lat,lng)")
    end_coordinates: str = Field(..., description="Destination coordinates (lat,lng)")
    price: float = Field(..., description="Ride price")
    max_riders: int = Field(..., description="Maximum number of riders")
    ride_date: datetime = Field(..., description="Date and time of the ride")
    is_recurring: bool = Field(False, description="Whether the ride is recurring")
    recurring_pattern: Optional[RecurringPatternRequest] = Field(None, description="Recurring pattern details")


class JoinRideRequest(BaseModel):
    """Request model for joining a ride"""
    ride_id: int = Field(..., description="ID of the ride to join")


class CloseRideRequest(BaseModel):
    """Request model for closing ride registration"""
    ride_id: int = Field(..., description="ID of the ride to close")


# User Request Models
class UpdateUserProfileRequest(BaseModel):
    """Request model for updating user profile"""
    name: Optional[str] = Field(None, description="User full name")
    phone: Optional[str] = Field(None, description="User phone number")
    email: Optional[str] = Field(None, description="User email")


class ChangePasswordRequest(BaseModel):
    """Request model for changing password"""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., description="New password")
    confirm_password: str = Field(..., description="Confirm new password")


# Driver Request Models
class UpdateDriverLicenseRequest(BaseModel):
    """Request model for updating driver license information"""
    license_number: str = Field(..., description="Driver's license number")
    license_expiry: datetime = Field(..., description="Driver's license expiry date")

