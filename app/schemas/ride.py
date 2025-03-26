from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum

class RideStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class Location(BaseModel):
    lat: float
    lng: float
    address: str

class RecurringPatternCreate(BaseModel):
    days_of_week: List[int]  # 1-7 representing Monday-Sunday
    start_date: datetime
    end_date: datetime

class RideCreate(BaseModel):
    driver_id: int
    start_location: Location
    end_location: Location
    waypoints: Optional[List[Location]] = None
    scheduled_for: Optional[datetime] = None
    is_recurring: bool = False
    recurring_pattern: Optional[Dict] = None
    notes: Optional[str] = None
    emergency_contact: Optional[Dict] = None

class RideUpdate(BaseModel):
    status: Optional[RideStatus] = None
    driver_id: Optional[int] = None
    pickup_time: Optional[datetime] = None
    dropoff_time: Optional[datetime] = None
    notes: Optional[str] = None

class RideResponse(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    status: RideStatus
    start_location: Location
    end_location: Location
    waypoints: Optional[List[Location]]
    distance_miles: float
    duration_minutes: int
    route_polyline: str
    route_steps: List[Dict]
    
    # Pricing
    base_price: float
    stop_fee: float
    time_fee: float
    platform_fee: float
    stripe_fees: float
    total_price: float
    driver_earnings: float
    
    # Scheduling
    scheduled_for: Optional[datetime]
    pickup_time: Optional[datetime]
    dropoff_time: Optional[datetime]
    
    # Relationships
    driver_id: Optional[int]
    creator_id: int
    
    # Additional Information
    number_of_stops: int
    is_recurring: bool
    recurring_pattern: Optional[Dict]
    notes: Optional[str]
    emergency_contact: Optional[Dict]
    verification_code: Optional[str]

    class Config:
        from_attributes = True
