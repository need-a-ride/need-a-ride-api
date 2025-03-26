from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class PriceCalculationRequest(BaseModel):
    distance_miles: float
    duration_minutes: int
    number_of_stops: int = 0
    is_recurring: bool = False
    current_gas_price: Optional[float] = None

class PriceBreakdown(BaseModel):
    total_price: float
    base_price: float
    stop_fee: float
    time_fee: float
    platform_fee: float  # This is now our actual profit
    driver_earnings: float
    price_per_mile: float
    price_per_rider: Optional[float] = None
    stripe_fees: float  # Added Stripe processing fees

class PriceCalculationResponse(BaseModel):
    status: str
    price_breakdown: PriceBreakdown
    error_message: Optional[str] = None

class RiderPriceRequest(BaseModel):
    total_price: float
    number_of_riders: int

class RiderPriceResponse(BaseModel):
    price_per_rider: float
    error_message: Optional[str] = None 
