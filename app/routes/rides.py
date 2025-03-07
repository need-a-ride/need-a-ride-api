from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Dict, Any, Optional, Tuple

from app.database.session import get_db
from app.schemas.ride import RideResponse
from app.schemas.response import (
    CreateRideResponse,
    GetRideResponse,
    RideActionResponse,
    RideListResponse,
    RideResponseData,
    RideActionResponseData,
    RideListResponseData,
    LocationResponse,
    StopResponse
)
from app.schemas.requests import (
    CreateRideRequest,
    JoinRideRequest,
    CloseRideRequest
)
from app.models.user import Driver, Customer
from app.models.ride import Ride, Location, RideStop, RecurringPattern
from app.models.car import Car
from app.services.ride_service import (
    create_ride,
    get_ride,
    join_ride,
    close_ride_registration,
    get_rides,
    get_total_rides_count
)
from app.services.auth_service import get_current_user, get_current_driver, get_current_customer
from app.services.maps_service import calculate_route, calculate_price_per_rider

router = APIRouter()


@router.post("/", response_model=CreateRideResponse)
async def create_ride_endpoint(
    ride: CreateRideRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Driver = Depends(get_current_driver),
):
    try:
        # Check if the driver has any cars
        result = await db.execute(select(Car).filter(Car.driver_id == current_user.id, Car.is_active == True))
        cars = result.scalars().all()
        
        if not cars:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You need to add a car before creating a ride. Please add a car first.",
                headers={"X-Error-Code": "NO_CARS_AVAILABLE"}
            )
        
        # Check if the specified car belongs to the driver
        car_result = await db.execute(
            select(Car).filter(
                Car.id == ride.car_id, 
                Car.driver_id == current_user.id,
                Car.is_active == True
            )
        )
        car = car_result.scalars().first()
        
        if not car:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The specified car does not exist or does not belong to you"
            )
        
        # Parse coordinates
        start_coords = tuple(map(float, ride.start_location.coordinates.split(",")))
        end_coords = tuple(map(float, ride.end_location.coordinates.split(",")))
        
        # Parse waypoints if provided
        waypoints = None
        has_stops = False
        if ride.stops and len(ride.stops) > 0:
            has_stops = True
            waypoints = [
                tuple(map(float, stop.location.coordinates.split(",")))
                for stop in ride.stops
            ]
        
        # Calculate route using Google Maps API
        route_info = await calculate_route(start_coords, end_coords, waypoints)
        
        if route_info.get("status") != "OK":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error calculating route: {route_info.get('error_message', 'Unknown error')}"
            )
        
        # Create or find start location
        start_location = Location(
            address=ride.start_location.address,
            latitude=start_coords[0],
            longitude=start_coords[1]
        )
        db.add(start_location)
        await db.flush()
        
        # Create or find end location
        end_location = Location(
            address=ride.end_location.address,
            latitude=end_coords[0],
            longitude=end_coords[1]
        )
        db.add(end_location)
        await db.flush()
        
        # Create the ride
        new_ride = Ride(
            driver_id=current_user.id,
            car_id=ride.car_id,
            start_location_id=start_location.id,
            end_location_id=end_location.id,
            price=route_info["recommended_price"],  # Use recommended price from Google Maps
            recommended_price=route_info["recommended_price"],
            max_riders=ride.max_riders,
            ride_date=ride.ride_date,
            distance_miles=route_info["distance_miles"],
            estimated_duration_minutes=route_info["duration_minutes"],
            is_recurring=ride.is_recurring,
            has_stops=has_stops
        )
        db.add(new_ride)
        await db.flush()
        
        # Create stops if provided
        if has_stops:
            for stop_request in ride.stops:
                stop_coords = tuple(map(float, stop_request.location.coordinates.split(",")))
                
                # Create location for stop
                stop_location = Location(
                    address=stop_request.location.address,
                    latitude=stop_coords[0],
                    longitude=stop_coords[1]
                )
                db.add(stop_location)
                await db.flush()
                
                # Create ride stop
                ride_stop = RideStop(
                    ride_id=new_ride.id,
                    location_id=stop_location.id,
                    stop_order=stop_request.stop_order
                )
                db.add(ride_stop)
        
        # Create recurring pattern if specified
        if ride.is_recurring and ride.recurring_pattern:
            pattern = RecurringPattern(
                days_of_week=",".join(map(str, ride.recurring_pattern.days_of_week)),
                start_date=ride.recurring_pattern.start_date,
                end_date=ride.recurring_pattern.end_date,
                ride_id=new_ride.id,
            )
            db.add(pattern)
        
        await db.commit()
        await db.refresh(new_ride)
        
        # Fetch the complete ride with all relationships
        complete_ride = await get_ride(db, new_ride.id)
        
        # Convert to response model
        response_data = await ride_to_response(db, complete_ride)
        
        return CreateRideResponse(data=response_data)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model=RideListResponse)
async def list_rides_endpoint(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db)
):
    rides = await get_rides(db, skip=(page - 1) * per_page, limit=per_page)
    total_count = await get_total_rides_count(db)
    total_pages = (total_count + per_page - 1) // per_page  # Ceiling division
    
    # Convert rides to response models
    ride_responses = []
    for ride in rides:
        ride_response = await ride_to_response(db, ride)
        ride_responses.append(ride_response)
    
    ride_list_data = RideListResponseData(
        items=ride_responses,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
        total_items=total_count
    )
    
    return RideListResponse(data=ride_list_data)


@router.get("/{ride_id}", response_model=GetRideResponse)
async def get_ride_endpoint(ride_id: int, db: AsyncSession = Depends(get_db)):
    ride = await get_ride(db, ride_id)
    if not ride:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ride with ID {ride_id} not found"
        )
    
    # Convert to response model
    response_data = await ride_to_response(db, ride)
    
    return GetRideResponse(data=response_data)


@router.post("/{ride_id}/join", response_model=RideActionResponse)
async def join_ride_endpoint(
    ride_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Customer = Depends(get_current_customer),
):
    try:
        result = await join_ride(db, ride_id, current_user.id)
        
        action_data = RideActionResponseData(
            ride_id=ride_id,
            status="joined"
        )
        
        return RideActionResponse(data=action_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{ride_id}/close", response_model=RideActionResponse)
async def close_ride_endpoint(
    ride_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Driver = Depends(get_current_driver),
):
    try:
        result = await close_ride_registration(db, ride_id, current_user.id)
        
        action_data = RideActionResponseData(
            ride_id=ride_id,
            status="closed"
        )
        
        return RideActionResponse(data=action_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


async def ride_to_response(db: AsyncSession, ride: Ride) -> RideResponseData:
    """Convert a Ride model to a RideResponseData"""
    # Calculate price per rider if there are riders
    price_per_rider = None
    if ride.current_riders > 0:
        price_per_rider = await calculate_price_per_rider(ride.price, ride.current_riders)
    
    # Get stops if any
    stops_response = []
    if ride.has_stops and ride.stops:
        for stop in ride.stops:
            stop_response = StopResponse(
                id=stop.id,
                location=LocationResponse(
                    id=stop.location.id,
                    address=stop.location.address,
                    latitude=stop.location.latitude,
                    longitude=stop.location.longitude,
                    formatted_address=stop.location.formatted_address
                ),
                stop_order=stop.stop_order
            )
            stops_response.append(stop_response)
    
    # Create response
    return RideResponseData(
        id=ride.id,
        driver_id=ride.driver_id,
        start_location=LocationResponse(
            id=ride.start_location.id,
            address=ride.start_location.address,
            latitude=ride.start_location.latitude,
            longitude=ride.start_location.longitude,
            formatted_address=ride.start_location.formatted_address
        ),
        end_location=LocationResponse(
            id=ride.end_location.id,
            address=ride.end_location.address,
            latitude=ride.end_location.latitude,
            longitude=ride.end_location.longitude,
            formatted_address=ride.end_location.formatted_address
        ),
        stops=stops_response,
        price=ride.price,
        recommended_price=ride.recommended_price,
        price_per_rider=price_per_rider,
        max_riders=ride.max_riders,
        current_riders=ride.current_riders,
        ride_date=ride.ride_date,
        registration_open=ride.registration_open,
        distance_miles=ride.distance_miles,
        estimated_duration_minutes=ride.estimated_duration_minutes,
        is_recurring=ride.is_recurring,
        has_stops=ride.has_stops,
        car=ride.car
    )
