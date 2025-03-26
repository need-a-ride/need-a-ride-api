from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime

class Location(BaseModel):
    lat: float
    lng: float

class Address(BaseModel):
    location: Location
    address: str

class RouteBounds(BaseModel):
    northeast: Location
    southwest: Location

class RouteSummary(BaseModel):
    start_location: Location
    end_location: Location
    start_address: str
    end_address: str
    bounds: RouteBounds
    copyrights: str
    stops: Optional[List[Address]] = None

class PriceBreakdown(BaseModel):
    total_price: float
    base_price: float
    stop_fee: float
    time_fee: float
    platform_fee: float
    driver_earnings: float
    price_per_mile: float
    price_per_rider: Optional[float] = None

class RouteResponse(BaseModel):
    status: str
    distance_miles: float
    duration_minutes: int
    recommended_price: float
    price_breakdown: PriceBreakdown
    polyline: str
    route_summary: RouteSummary
    stops: List[Address]
    error_message: Optional[str] = None

class RouteRequest(BaseModel):
    start_coords: Tuple[float, float]
    end_coords: Tuple[float, float]
    waypoints: Optional[List[Tuple[float, float]]] = None 
