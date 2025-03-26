import os
from typing import List, Optional, Tuple
import aiogmaps
import logging
from app.services.price_service import calculate_ride_price, calculate_price_per_rider
from app.schemas.maps import (
    RouteRequest,
    RouteResponse,
    Location,
    Address,
    RouteBounds,
    RouteSummary,
    PriceBreakdown
)
from app.core.config import settings
from app.models.location import Location as LocationModel
from sqlalchemy.orm import Session
from googlemaps import Client
from app.core.maps import calculate_route, geocode_address, reverse_geocode
from app.core.location import LocationService

# Initialize Google Maps client
gmaps_client = None
logger = logging.getLogger(__name__)
gmaps = Client(key=settings.GOOGLE_MAPS_API_KEY)

def get_gmaps_client():
    global gmaps_client
    if gmaps_client is None:
        api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_MAPS_API_KEY environment variable is not set")
        gmaps_client = aiogmaps.Client(key=api_key)
    return gmaps_client

async def calculate_ride_route(
    start_coords: Tuple[float, float],
    end_coords: Tuple[float, float],
    waypoints: Optional[List[Tuple[float, float]]] = None
) -> Optional[RouteResponse]:
    """
    Calculate a route for a ride with optional waypoints
    """
    return await calculate_route(start_coords, end_coords, waypoints)

async def get_coordinates_from_address(address: str) -> Optional[Tuple[float, float]]:
    """
    Get coordinates from an address
    """
    return await geocode_address(address)

async def get_address_from_coordinates(coords: Tuple[float, float]) -> Optional[str]:
    """
    Get formatted address from coordinates
    """
    return await reverse_geocode(coords)

async def calculate_price_per_rider(total_price: float, number_of_riders: int) -> float:
    """
    Calculate the price per rider when splitting the cost
    """
    return await calculate_price_per_rider(total_price, number_of_riders)

async def calculate_route(
    start_coords: Tuple[float, float],
    end_coords: Tuple[float, float],
    waypoints: Optional[List[Tuple[float, float]]] = None
) -> Optional[RouteResponse]:
    """
    Calculate a route between two points with optional waypoints
    """
    try:
        # Format coordinates for Google Maps API
        origin = f"{start_coords[0]},{start_coords[1]}"
        destination = f"{end_coords[0]},{end_coords[1]}"
        
        # Format waypoints if provided
        formatted_waypoints = []
        if waypoints:
            formatted_waypoints = [
                f"{wp[0]},{wp[1]}" for wp in waypoints
            ]

        # Request directions from Google Maps API
        directions_result = gmaps.directions(
            origin=origin,
            destination=destination,
            waypoints=formatted_waypoints if formatted_waypoints else None,
            mode="driving",
            alternatives=False
        )

        if not directions_result:
            return None

        route = directions_result[0]
        leg = route['legs'][0]

        # Calculate total distance and duration
        total_distance = sum(leg['distance']['value'] for leg in route['legs'])
        total_duration = sum(leg['duration']['value'] for leg in route['legs'])

        # Create route summary
        route_summary = RouteSummary(
            start_location=Address(
                location=Location(
                    lat=route['bounds']['northeast']['lat'],
                    lng=route['bounds']['northeast']['lng']
                ),
                address=leg['start_address']
            ),
            end_location=Address(
                location=Location(
                    lat=route['bounds']['southwest']['lat'],
                    lng=route['bounds']['southwest']['lng']
                ),
                address=leg['end_address']
            ),
            bounds={
                'northeast': {
                    'lat': route['bounds']['northeast']['lat'],
                    'lng': route['bounds']['northeast']['lng']
                },
                'southwest': {
                    'lat': route['bounds']['southwest']['lat'],
                    'lng': route['bounds']['southwest']['lng']
                }
            },
            copyrights=route['copyrights']
        )

        # Create price breakdown
        price_breakdown = PriceBreakdown(
            base_price=0.0,  # Will be calculated by price service
            stop_fee=0.0,
            time_fee=0.0,
            platform_fee=0.0,
            stripe_fees=0.0,
            total_price=0.0,
            driver_earnings=0.0
        )

        return RouteResponse(
            status="success",
            distance_miles=total_distance * 0.000621371,  # Convert meters to miles
            duration_minutes=total_duration // 60,  # Convert seconds to minutes
            route_polyline=route['overview_polyline']['points'],
            route_steps=route['legs'][0]['steps'],
            route_summary=route_summary,
            price_breakdown=price_breakdown
        )

    except Exception as e:
        return RouteResponse(
            status="error",
            error_message=str(e)
        )

async def geocode_address(address: str) -> Optional[Tuple[float, float]]:
    """
    Convert an address to coordinates
    """
    try:
        result = gmaps.geocode(address)
        if result:
            location = result[0]['geometry']['location']
            return (location['lat'], location['lng'])
        return None
    except Exception:
        return None

async def reverse_geocode(coords: Tuple[float, float]) -> Optional[str]:
    """
    Convert coordinates to an address
    """
    try:
        result = gmaps.reverse_geocode(coords)
        if result:
            return result[0]['formatted_address']
        return None
    except Exception:
        return None

async def get_or_create_location(
    db: Session,
    address: str,
    latitude: float,
    longitude: float,
    formatted_address: Optional[str] = None
) -> LocationModel:
    """
    Get an existing location or create a new one
    """
    # Try to find existing location
    location = db.query(LocationModel).filter(
        LocationModel.latitude == latitude,
        LocationModel.longitude == longitude
    ).first()

    if not location:
        # Create new location if not found
        if not formatted_address:
            formatted_address = await reverse_geocode((latitude, longitude))
        
        location = LocationModel(
            address=address,
            latitude=latitude,
            longitude=longitude,
            formatted_address=formatted_address
        )
        db.add(location)
        db.flush()
        db.refresh(location)

    return location
