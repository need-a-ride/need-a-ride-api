import os
from typing import List, Optional
import aiogmaps
import logging
from app.services.price_service import calculate_ride_price
from app.schemas.maps import (
    RouteRequest,
    RouteResponse,
    Location,
    Address,
    RouteBounds,
    RouteSummary,
    PriceBreakdown
)

# Initialize Google Maps client
gmaps_client = None
logger = logging.getLogger(__name__)

def get_gmaps_client():
    global gmaps_client
    if gmaps_client is None:
        api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_MAPS_API_KEY environment variable is not set")
        gmaps_client = aiogmaps.Client(key=api_key)
    return gmaps_client

async def calculate_route(
    request: RouteRequest
) -> RouteResponse:
    """
    Calculate car route, distance, duration, and price using Google Maps API
    """
    try:
        # Format coordinates for Google Maps API
        origin = f"{request.start_coords[0]},{request.start_coords[1]}"
        destination = f"{request.end_coords[0]},{request.end_coords[1]}"
        
        # Format waypoints if provided
        formatted_waypoints = None
        if request.waypoints:
            formatted_waypoints = [
                f"{wp[0]},{wp[1]}"
                for wp in request.waypoints
            ]
        
        # Get Google Maps client
        gmaps = get_gmaps_client()
        
        # Calculate route specifically for driving
        directions_result = await gmaps.directions(
            origin=origin,
            destination=destination,
            waypoints=formatted_waypoints,
            mode="driving",  # Specifically request driving directions
            optimize_waypoints=True,
            departure_time="now",  # Use current time for traffic information
            alternatives=False  # We only need the best route for driving
        )
        
        if not directions_result:
            return RouteResponse(
                status="ERROR",
                distance_miles=0,
                duration_minutes=0,
                recommended_price=0,
                price_breakdown=PriceBreakdown(
                    total_price=0,
                    base_price=0,
                    stop_fee=0,
                    time_fee=0,
                    platform_fee=0,
                    driver_earnings=0,
                    price_per_mile=0
                ),
                polyline="",
                route_summary=RouteSummary(
                    start_location=Location(lat=0, lng=0),
                    end_location=Location(lat=0, lng=0),
                    start_address="",
                    end_address="",
                    bounds=RouteBounds(
                        northeast=Location(lat=0, lng=0),
                        southwest=Location(lat=0, lng=0)
                    ),
                    copyrights="",
                    stops=[]
                ),
                stops=[],
                error_message="No route found"
            )
        
        # Get the best driving route
        route = directions_result[0]
        
        # Get the route summary
        route_summary = route['routes'][0]
        
        # Calculate total distance and duration
        distance_meters = route_summary['distance']['value']
        duration_seconds = route_summary['duration']['value']
        
        # Convert to miles and minutes
        distance_miles = distance_meters / 1609.34
        duration_minutes = duration_seconds / 60
        
        # Calculate price using our price service
        price_info = await calculate_ride_price(
            distance_miles=distance_miles,
            duration_minutes=int(duration_minutes),
            number_of_stops=len(request.waypoints) if request.waypoints else 0
        )
        
        # Create route summary
        summary = RouteSummary(
            start_location=Location(**route_summary['start_location']),
            end_location=Location(**route_summary['end_location']),
            start_address=route_summary['start_address'],
            end_address=route_summary['end_address'],
            bounds=RouteBounds(
                northeast=Location(**route_summary['bounds']['northeast']),
                southwest=Location(**route_summary['bounds']['southwest'])
            ),
            copyrights=route_summary['copyrights'],
            stops=[
                Address(
                    location=Location(**stop['location']),
                    address=stop['address']
                )
                for stop in route_summary.get('stops', [])
            ]
        )
        
        return RouteResponse(
            status="OK",
            distance_miles=round(distance_miles, 2),
            duration_minutes=int(duration_minutes),
            recommended_price=price_info.total_price,
            price_breakdown=price_info,
            polyline=route['overview_polyline']['points'],
            route_summary=summary,
            stops=summary.stops or []
        )
        
    except Exception as e:
        logger.error(f"Error calculating route: {e}")
        return RouteResponse(
            status="ERROR",
            distance_miles=0,
            duration_minutes=0,
            recommended_price=0,
            price_breakdown=PriceBreakdown(
                total_price=0,
                base_price=0,
                stop_fee=0,
                time_fee=0,
                platform_fee=0,
                driver_earnings=0,
                price_per_mile=0
            ),
            polyline="",
            route_summary=RouteSummary(
                start_location=Location(lat=0, lng=0),
                end_location=Location(lat=0, lng=0),
                start_address="",
                end_address="",
                bounds=RouteBounds(
                    northeast=Location(lat=0, lng=0),
                    southwest=Location(lat=0, lng=0)
                ),
                copyrights="",
                stops=[]
            ),
            stops=[],
            error_message=str(e)
        )

async def calculate_price_per_rider(total_price: float, number_of_riders: int) -> float:
    """
    Calculate the price per rider when splitting the cost
    """
    from app.services.price_service import calculate_price_per_rider as calculate_rider_price
    return await calculate_rider_price(total_price, number_of_riders)
