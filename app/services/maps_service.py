import os
import httpx
from typing import List, Tuple, Dict, Any, Optional
import logging

# Get Google Maps API key from environment variables
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
DIRECTIONS_API_URL = "https://maps.googleapis.com/maps/api/directions/json"
PRICE_PER_MILE = 1.0  # $1 per mile

logger = logging.getLogger(__name__)


async def calculate_route(
    origin: Tuple[float, float],
    destination: Tuple[float, float],
    waypoints: Optional[List[Tuple[float, float]]] = None
) -> Dict[str, Any]:
    """
    Calculate route information using Google Maps Directions API
    
    Args:
        origin: Tuple of (latitude, longitude) for the starting point
        destination: Tuple of (latitude, longitude) for the ending point
        waypoints: Optional list of (latitude, longitude) tuples for intermediate stops
        
    Returns:
        Dictionary containing route information:
        {
            "distance_miles": float,
            "duration_minutes": int,
            "recommended_price": float,
            "polyline": str,  # Encoded polyline for the route
            "steps": list,    # List of steps in the route
            "status": str     # Status of the API request
        }
    """
    if not GOOGLE_MAPS_API_KEY:
        logger.error("Google Maps API key not found in environment variables")
        raise ValueError("Google Maps API key not configured")
    
    # Format origin and destination as "lat,lng"
    origin_str = f"{origin[0]},{origin[1]}"
    destination_str = f"{destination[0]},{destination[1]}"
    
    # Prepare request parameters
    params = {
        "origin": origin_str,
        "destination": destination_str,
        "key": GOOGLE_MAPS_API_KEY,
        "mode": "driving",
    }
    
    # Add waypoints if provided
    if waypoints and len(waypoints) > 0:
        waypoints_str = "|".join([f"{wp[0]},{wp[1]}" for wp in waypoints])
        params["waypoints"] = waypoints_str
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(DIRECTIONS_API_URL, params=params)
            response.raise_for_status()  # Raise exception for HTTP errors
            
            data = response.json()
            
            if data["status"] != "OK":
                logger.error(f"Google Maps API error: {data['status']}")
                return {
                    "status": data["status"],
                    "error_message": data.get("error_message", "Unknown error")
                }
            
            # Extract route information
            route = data["routes"][0]
            leg = route["legs"][0]  # First leg of the route
            
            # Calculate total distance and duration
            distance_meters = sum(step["distance"]["value"] for step in leg["steps"])
            duration_seconds = sum(step["duration"]["value"] for step in leg["steps"])
            
            # Convert to miles and minutes
            distance_miles = distance_meters / 1609.34  # 1 mile = 1609.34 meters
            duration_minutes = duration_seconds // 60
            
            # Calculate recommended price
            recommended_price = distance_miles * PRICE_PER_MILE
            
            return {
                "distance_miles": round(distance_miles, 2),
                "duration_minutes": int(duration_minutes),
                "recommended_price": round(recommended_price, 2),
                "polyline": route["overview_polyline"]["points"],
                "steps": leg["steps"],
                "status": "OK"
            }
    
    except httpx.HTTPError as e:
        logger.error(f"HTTP error occurred: {e}")
        return {
            "status": "HTTP_ERROR",
            "error_message": str(e)
        }
    except Exception as e:
        logger.error(f"Error calculating route: {e}")
        return {
            "status": "ERROR",
            "error_message": str(e)
        }


async def calculate_price_per_rider(base_price: float, num_riders: int) -> float:
    """
    Calculate the price per rider based on the total price and number of riders
    
    Args:
        base_price: The total ride price
        num_riders: Number of riders (excluding driver)
        
    Returns:
        Price per rider
    """
    if num_riders <= 0:
        return base_price  # If no riders, the full price applies
    
    return round(base_price / num_riders, 2) 
