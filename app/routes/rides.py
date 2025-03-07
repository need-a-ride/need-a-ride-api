from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Dict, Any, Optional
from app.database.session import get_db
from app.schemas.ride import RideResponse
from app.schemas.response import (
    CreateRideResponse,
    GetRideResponse,
    RideActionResponse,
    RideListResponse,
    CreateRideResponseData,
    GetRideResponseData,
    RideActionResponseData,
    RideListResponseData
)
from app.schemas.requests import (
    CreateRideRequest,
    JoinRideRequest,
    CloseRideRequest
)
from app.models.user import Driver, Customer
from app.models.ride import Ride
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
        
        # Create the ride
        new_ride = await create_ride(db, ride, current_user.id)
        return CreateRideResponse(data=new_ride)
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
    
    ride_list_data = RideListResponseData(
        items=rides,
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
    
    return GetRideResponse(data=ride)


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
