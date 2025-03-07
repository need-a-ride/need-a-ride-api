from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class RecurringPatternCreate(BaseModel):
    days_of_week: List[int]  # 1-7 representing Monday-Sunday
    start_date: datetime
    end_date: datetime


class RideCreate(BaseModel):
    driver_id: int
    start_location: str
    end_location: str
    start_coordinates: str  # "lat,lng"
    end_coordinates: str  # "lat,lng"
    price: float
    max_riders: int
    ride_date: datetime
    is_recurring: bool = False
    recurring_pattern: Optional[RecurringPatternCreate] = None


class RideResponse(BaseModel):
    id: int
    driver_id: int
    start_location: str
    end_location: str
    price: float
    recommended_price: float
    max_riders: int
    current_riders: int
    ride_date: datetime
    registration_open: bool
    distance_miles: float
    is_recurring: bool
