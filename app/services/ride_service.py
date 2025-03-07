from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select, func
from datetime import datetime
from typing import List, Optional
from app.models.ride import Ride, RecurringPattern, RideRiders
from app.schemas.requests import CreateRideRequest
from app.core.estimator import get_route, calculate_nearest_distance
from app.services.location_service import LocationService


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
    route = get_route(
        (start_location.latitude, start_location.longitude),
        (end_location.latitude, end_location.longitude),
    )
    distance = calculate_nearest_distance(route)
    recommended_price = distance * 1.0  # $1 per mile

    # Create the ride
    db_ride = Ride(
        driver_id=driver_id,
        start_location_id=start_location.id,
        end_location_id=end_location.id,
        price=ride.price,
        recommended_price=recommended_price,
        max_riders=ride.max_riders,
        ride_date=ride.ride_date,
        distance_miles=distance,
        is_recurring=ride.is_recurring,
    )
    db.add(db_ride)
    await db.commit()
    await db.refresh(db_ride)

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
    query = select(Ride)
    
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


async def get_ride(db: AsyncSession, ride_id: int):
    result = await db.execute(select(Ride).filter(Ride.id == ride_id))
    return result.scalars().first()


async def join_ride(db: AsyncSession, ride_id: int, customer_id: int):
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
    return ride


async def close_ride_registration(db: AsyncSession, ride_id: int, driver_id: int):
    ride = await get_ride(db, ride_id)
    if not ride or ride.driver_id != driver_id:
        raise ValueError("Unauthorized or ride not found")

    ride.registration_open = False
    if ride.current_riders > 0:
        # Calculate split price
        split_price = ride.price / ride.current_riders  # +1 for driver
        # Update payment information (you'll need to implement this)
        # TODO: Implement payment information update

    await db.commit()
    return ride
