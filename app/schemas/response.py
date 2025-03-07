from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from app.schemas.user import UserResponse
from app.schemas.ride import RideResponse


# Location Response Models
class LocationResponse(BaseModel):
    """Location data returned in responses"""
    id: int = Field(..., description="Location ID")
    address: str = Field(..., description="Location address")
    latitude: float = Field(..., description="Location latitude")
    longitude: float = Field(..., description="Location longitude")
    formatted_address: Optional[str] = Field(None, description="Formatted address")


class StopResponse(BaseModel):
    """Stop data returned in responses"""
    id: int = Field(..., description="Stop ID")
    location: LocationResponse = Field(..., description="Stop location")
    stop_order: int = Field(..., description="Order of the stop in the ride")


# Car Response Models
class CarResponse(BaseModel):
    """Car data returned in responses"""
    id: int = Field(..., description="Car ID")
    make: str = Field(..., description="Car manufacturer")
    model: str = Field(..., description="Car model")
    year: int = Field(..., description="Car year of manufacture")
    color: str = Field(..., description="Car color")
    license_plate: str = Field(..., description="Car license plate number")
    capacity: int = Field(..., description="Car passenger capacity")
    air_conditioned: bool = Field(..., description="Whether the car has air conditioning")
    has_wheelchair_access: bool = Field(..., description="Whether the car has wheelchair access")
    is_active: bool = Field(..., description="Whether the car is active")


# Auth Response Models
class UserProfileResponse(BaseModel):
    """User profile data returned in authentication responses"""
    id: int = Field(..., description="User ID")
    email: str = Field(..., description="User email")
    name: str = Field(..., description="User name")
    phone: str = Field(..., description="User phone number")
    profile_picture: Optional[str] = Field(None, description="User profile picture URL")
    user_type: str = Field(..., description="Type of user (driver or customer)")
    # Driver-specific fields
    is_verified: Optional[bool] = Field(None, description="Whether the driver is verified")
    license_number: Optional[str] = Field(None, description="Driver's license number")
    license_expiry: Optional[datetime] = Field(None, description="Driver's license expiry date")


class LoginResponseData(BaseModel):
    """Data structure returned by login endpoint"""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field("bearer", description="Token type")
    user: UserProfileResponse = Field(..., description="User profile information")


class RegisterResponseData(BaseModel):
    """Data structure returned by register endpoint"""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field("bearer", description="Token type")
    user: UserProfileResponse = Field(..., description="User profile information")


class RefreshTokenResponseData(BaseModel):
    """Data structure returned by token refresh endpoint"""
    access_token: str = Field(..., description="New JWT access token")
    refresh_token: str = Field(..., description="New JWT refresh token")
    token_type: str = Field("bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")


class LogoutResponseData(BaseModel):
    """Data structure returned by logout endpoint"""
    message: str = Field(..., description="Logout status message")


# Ride Response Models
class RideResponseData(BaseModel):
    """Base ride data returned in responses"""
    id: int = Field(..., description="Ride ID")
    driver_id: int = Field(..., description="Driver ID")
    start_location: LocationResponse = Field(..., description="Starting location")
    end_location: LocationResponse = Field(..., description="Destination location")
    stops: Optional[List[StopResponse]] = Field([], description="Intermediate stops")
    price: float = Field(..., description="Ride price")
    recommended_price: float = Field(..., description="Recommended price based on distance")
    price_per_rider: Optional[float] = Field(None, description="Price per rider (if ride has riders)")
    max_riders: int = Field(..., description="Maximum number of riders")
    current_riders: int = Field(..., description="Current number of riders")
    ride_date: datetime = Field(..., description="Date and time of the ride")
    registration_open: bool = Field(..., description="Whether registration is open")
    distance_miles: float = Field(..., description="Ride distance in miles")
    estimated_duration_minutes: int = Field(..., description="Estimated travel time in minutes")
    is_recurring: bool = Field(..., description="Whether the ride is recurring")
    has_stops: bool = Field(..., description="Whether the ride has intermediate stops")
    car: CarResponse = Field(..., description="Car used for this ride")


class PriceEstimateResponseData(BaseModel):
    """Data structure returned by price estimate endpoint"""
    distance_miles: float = Field(..., description="Estimated distance in miles")
    estimated_duration_minutes: int = Field(..., description="Estimated travel time in minutes")
    recommended_price: float = Field(..., description="Recommended price based on distance")
    polyline: str = Field(..., description="Encoded polyline for the route")


class RideActionResponseData(BaseModel):
    """Data structure returned by ride action endpoints (join, close)"""
    ride_id: int = Field(..., description="Ride ID")
    status: str = Field(..., description="Action status")


class RideListResponseData(BaseModel):
    """Data structure returned by list rides endpoint"""
    items: List[RideResponseData] = Field(..., description="List of rides")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")
    total_items: int = Field(..., description="Total number of items")


# Error Response Models
class ValidationErrorItem(BaseModel):
    """Individual validation error"""
    loc: List[str] = Field(..., description="Location of error")
    msg: str = Field(..., description="Error message")
    type: str = Field(..., description="Error type")


class ValidationErrorResponse(BaseModel):
    """Response structure for validation errors"""
    detail: List[ValidationErrorItem] = Field(..., description="List of validation errors")


class ErrorResponseData(BaseModel):
    """Response structure for application errors"""
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")


# Complete Response Models for API Documentation
class LoginResponse(BaseModel):
    """Complete response model for login endpoint"""
    data: LoginResponseData


class RegisterResponse(BaseModel):
    """Complete response model for register endpoint"""
    data: RegisterResponseData


class RefreshTokenResponse(BaseModel):
    """Complete response model for token refresh endpoint"""
    data: RefreshTokenResponseData


class LogoutResponse(BaseModel):
    """Complete response model for logout endpoint"""
    data: LogoutResponseData


class CreateRideResponse(BaseModel):
    """Complete response model for create ride endpoint"""
    data: RideResponseData


class GetRideResponse(BaseModel):
    """Complete response model for get ride endpoint"""
    data: RideResponseData


class PriceEstimateResponse(BaseModel):
    """Complete response model for price estimate endpoint"""
    data: PriceEstimateResponseData


class RideActionResponse(BaseModel):
    """Complete response model for ride action endpoints"""
    data: RideActionResponseData


class RideListResponse(BaseModel):
    """Complete response model for list rides endpoint"""
    data: RideListResponseData


class ErrorResponse(BaseModel):
    """Complete response model for error responses"""
    error: ErrorResponseData


class CarListResponse(BaseModel):
    """Complete response model for list cars endpoint"""
    data: List[CarResponse]


class CarDetailResponse(BaseModel):
    """Complete response model for get car endpoint"""
    data: CarResponse 

