from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select, func
from sqlalchemy.orm import joinedload
from datetime import datetime
from typing import List, Optional, Tuple, Dict
from app.models.ride import Ride, RecurringPattern, RideRiders, Location, RideStop, RideStatus
from app.models.car import Car
from app.schemas.requests import CreateRideRequest
from app.core.location import LocationService
from app.core.maps import calculate_route
from app.services.price_service import calculate_ride_price
from app.core.security import generate_verification_code
import json


async def create_ride(db: AsyncSession, ride: CreateRideRequest, driver_id: int):
    location_service = LocationService(db)

    # Create or find locations
    start_coords = tuple(map(float, ride.start_coordinates.split(",")))
    end_coords = tuple(map(float, ride.end_coordinates.split(",")))

    start_location = await location_service.find_or_create_location(
        address=ride.start_location, latitude=start_coords[0], longitude=start_coords[1]
    )

    end_location = await location_service.find_or_create_location(
        address=ride.end_location, latitude=end_coords[0], longitude=end_coords[1]
    )

    # Calculate route and recommended price
    route = await calculate_route(
        start_coords=(start_location.latitude, start_location.longitude),
        end_coords=(end_location.latitude, end_location.longitude)
    )
    
    if not route or route.status != "success":
        raise ValueError("Could not calculate route")

    # Calculate price
    price_info = await calculate_ride_price(
        distance_miles=route.distance_miles,
        duration_minutes=route.duration_minutes,
        number_of_stops=len(ride.stops) if ride.stops else 0
    )

    # Create the ride
    db_ride = Ride(
        driver_id=driver_id,
        start_location_id=start_location.id,
        end_location_id=end_location.id,
        distance_miles=route.distance_miles,
        duration_minutes=route.duration_minutes,
        route_polyline=route.route_polyline,
        route_steps=json.dumps(route.route_steps),
        base_price=price_info.base_price,
        stop_fee=price_info.stop_fee,
        time_fee=price_info.time_fee,
        platform_fee=price_info.platform_fee,
        stripe_fees=price_info.stripe_fees,
        total_price=price_info.total_price,
        driver_earnings=price_info.driver_earnings,
        scheduled_for=ride.ride_date,
        number_of_stops=len(ride.stops) if ride.stops else 0,
        is_recurring=ride.is_recurring,
        notes=ride.notes,
        emergency_contact=json.dumps(ride.emergency_contact) if ride.emergency_contact else None,
        verification_code=generate_verification_code()
    )
    db.add(db_ride)
    await db.flush()

    # Create stops if provided
    if ride.stops:
        for i, stop in enumerate(ride.stops, 1):
            stop_coords = tuple(map(float, stop.coordinates.split(",")))
            stop_location = await location_service.find_or_create_location(
                address=stop.address,
                latitude=stop_coords[0],
                longitude=stop_coords[1]
            )
            
            ride_stop = RideStop(
                ride_id=db_ride.id,
                location_id=stop_location.id,
                stop_order=i
            )
            db.add(ride_stop)

    # Create recurring pattern if specified
    if ride.is_recurring and ride.recurring_pattern:
        pattern = RecurringPattern(
            days_of_week=",".join(map(str, ride.recurring_pattern.days_of_week)),
            start_date=ride.recurring_pattern.start_date,
            end_date=ride.recurring_pattern.end_date,
            ride_id=db_ride.id,
        )
        db.add(pattern)

    await db.commit()
    await db.refresh(db_ride)
    return db_ride


async def get_rides(
    db: AsyncSession, 
    skip: int = 0, 
    limit: int = 10,
    driver_id: Optional[int] = None,
    upcoming_only: bool = False
) -> List[Ride]:
    """
    Get a paginated list of rides with optional filtering
    
    Args:
        db: Database session
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
        driver_id: Filter by driver ID (optional)
        upcoming_only: If True, only return rides in the future
        
    Returns:
        List of Ride objects
    """
    query = select(Ride).options(
        joinedload(Ride.start_location),
        joinedload(Ride.end_location),
        joinedload(Ride.car),
        joinedload(Ride.stops).joinedload(RideStop.location)
    )
    
    # Apply filters
    if driver_id is not None:
        query = query.filter(Ride.driver_id == driver_id)
        
    if upcoming_only:
        query = query.filter(Ride.ride_date >= datetime.now())
    
    # Apply pagination
    query = query.offset(skip).limit(limit)
    
    # Execute query
    result = await db.execute(query)
    return result.scalars().all()


async def get_total_rides_count(
    db: AsyncSession,
    driver_id: Optional[int] = None,
    upcoming_only: bool = False
) -> int:
    """
    Get the total count of rides with optional filtering
    
    Args:
        db: Database session
        driver_id: Filter by driver ID (optional)
        upcoming_only: If True, only count rides in the future
        
    Returns:
        Total count of rides matching the filters
    """
    query = select(func.count()).select_from(Ride)
    
    # Apply filters
    if driver_id is not None:
        query = query.filter(Ride.driver_id == driver_id)
        
    if upcoming_only:
        query = query.filter(Ride.ride_date >= datetime.now())
    
    # Execute query
    result = await db.execute(query)
    return result.scalar()


async def get_ride(db: AsyncSession, ride_id: int) -> Optional[Ride]:
    """
    Get a ride by ID with all related data
    
    Args:
        db: Database session
        ride_id: ID of the ride to retrieve
        
    Returns:
        Ride object or None if not found
    """
    query = select(Ride).options(
        joinedload(Ride.start_location),
        joinedload(Ride.end_location),
        joinedload(Ride.car),
        joinedload(Ride.stops).joinedload(RideStop.location)
    ).filter(Ride.id == ride_id)
    
    result = await db.execute(query)
    return result.scalars().first()


async def join_ride(db: AsyncSession, ride_id: int, customer_id: int) -> Ride:
    """
    Join a ride as a customer
    
    Args:
        db: Database session
        ride_id: ID of the ride to join
        customer_id: ID of the customer joining the ride
        
    Returns:
        Updated Ride object
    """
    ride = await get_ride(db, ride_id)
    if not ride:
        raise ValueError("Ride not found")
    if not ride.registration_open:
        raise ValueError("Ride registration is closed")
    if ride.current_riders >= ride.max_riders:
        raise ValueError("Ride is full")

    # Check if user is already registered for this ride
    result = await db.execute(
        select(RideRiders).filter(
            RideRiders.ride_id == ride_id,
            RideRiders.rider_id == customer_id
        )
    )
    existing_registration = result.scalars().first()
    if existing_registration:
        raise ValueError("You are already registered for this ride")

    rider_entry = RideRiders(ride_id=ride_id, rider_id=customer_id)
    db.add(rider_entry)
    ride.current_riders += 1
    await db.commit()
    await db.refresh(ride)
    return ride


async def close_ride_registration(db: AsyncSession, ride_id: int, driver_id: int) -> Ride:
    """
    Close registration for a ride and calculate final price per rider
    
    Args:
        db: Database session
        ride_id: ID of the ride to close
        driver_id: ID of the driver (for authorization)
        
    Returns:
        Updated Ride object
    """
    ride = await get_ride(db, ride_id)
    if not ride or ride.driver_id != driver_id:
        raise ValueError("Unauthorized or ride not found")

    ride.registration_open = False
    
    # Calculate price per rider if there are riders
    if ride.current_riders > 0:
        # Price is already set based on distance, no need to recalculate
        # Just update the payment information if needed
        pass
    
    await db.commit()
    await db.refresh(ride)
    return ride


async def update_ride(db: AsyncSession, ride_id: int, ride_update: RideUpdate) -> Optional[Ride]:
    """
    Update a ride's status or details
    """
    db_ride = await get_ride(db, ride_id)
    if not db_ride:
        return None
    
    update_data = ride_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_ride, field, value)
    
    await db.commit()
    await db.refresh(db_ride)
    return db_ride


async def get_user_rides(
    db: AsyncSession,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    status: Optional[RideStatus] = None
) -> List[Ride]:
    """
    Get rides for a user (either as creator or driver)
    """
    query = select(Ride).filter(
        (Ride.creator_id == user_id) | (Ride.driver_id == user_id)
    )
    
    if status:
        query = query.filter(Ride.status == status)
    
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()


async def accept_ride(db: AsyncSession, ride_id: int, driver_id: int) -> Optional[Ride]:
    """
    Accept a ride as a driver
    """
    db_ride = await get_ride(db, ride_id)
    if not db_ride or db_ride.status != RideStatus.PENDING:
        return None
    
    db_ride.status = RideStatus.ACCEPTED
    db_ride.driver_id = driver_id
    await db.commit()
    await db.refresh(db_ride)
    return db_ride


async def start_ride(db: AsyncSession, ride_id: int) -> Optional[Ride]:
    """
    Start a ride
    """
    db_ride = await get_ride(db, ride_id)
    if not db_ride or db_ride.status != RideStatus.ACCEPTED:
        return None
    
    db_ride.status = RideStatus.IN_PROGRESS
    db_ride.pickup_time = datetime.utcnow()
    await db.commit()
    await db.refresh(db_ride)
    return db_ride


async def complete_ride(db: AsyncSession, ride_id: int) -> Optional[Ride]:
    """
    Complete a ride
    """
    db_ride = await get_ride(db, ride_id)
    if not db_ride or db_ride.status != RideStatus.IN_PROGRESS:
        return None
    
    db_ride.status = RideStatus.COMPLETED
    db_ride.dropoff_time = datetime.utcnow()
    await db.commit()
    await db.refresh(db_ride)
    return db_ride


async def cancel_ride(db: AsyncSession, ride_id: int) -> Optional[Ride]:
    """
    Cancel a ride
    """
    db_ride = await get_ride(db, ride_id)
    if not db_ride or db_ride.status not in [RideStatus.PENDING, RideStatus.ACCEPTED]:
        return None
    
    db_ride.status = RideStatus.CANCELLED
    await db.commit()
    await db.refresh(db_ride)
    return db_ride
