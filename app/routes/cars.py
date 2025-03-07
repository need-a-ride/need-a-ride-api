from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from app.database.session import get_db
from app.models.car import Car
from app.schemas.response import (
    CarResponse,
    CarListResponse,
    CarDetailResponse
)
from app.schemas.requests import (
    CarCreateRequest,
    CarUpdateRequest
)
from app.services.auth_service import get_current_driver

router = APIRouter()


@router.post("/", response_model=CarDetailResponse)
async def create_car(
    car: CarCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_driver = Depends(get_current_driver)
):
    """Create a new car for the current driver"""
    # Check if license plate already exists
    result = await db.execute(select(Car).filter(Car.license_plate == car.license_plate))
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="License plate already registered"
        )
    
    # Create new car
    db_car = Car(
        driver_id=current_driver.id,
        make=car.make,
        model=car.model,
        year=car.year,
        color=car.color,
        license_plate=car.license_plate,
        capacity=car.capacity,
        air_conditioned=car.air_conditioned,
        has_wheelchair_access=car.has_wheelchair_access
    )
    
    db.add(db_car)
    await db.commit()
    await db.refresh(db_car)
    
    return CarDetailResponse(data=db_car)


@router.get("/", response_model=CarListResponse)
async def list_cars(
    db: AsyncSession = Depends(get_db),
    current_driver = Depends(get_current_driver)
):
    """List all cars for the current driver"""
    result = await db.execute(select(Car).filter(Car.driver_id == current_driver.id))
    cars = result.scalars().all()
    
    return CarListResponse(data=cars)


@router.get("/{car_id}", response_model=CarDetailResponse)
async def get_car(
    car_id: int,
    db: AsyncSession = Depends(get_db),
    current_driver = Depends(get_current_driver)
):
    """Get a specific car by ID"""
    result = await db.execute(
        select(Car).filter(Car.id == car_id, Car.driver_id == current_driver.id)
    )
    car = result.scalars().first()
    
    if not car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Car with ID {car_id} not found"
        )
    
    return CarDetailResponse(data=car)


@router.put("/{car_id}", response_model=CarDetailResponse)
async def update_car(
    car_id: int,
    car_update: CarUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_driver = Depends(get_current_driver)
):
    """Update a specific car by ID"""
    result = await db.execute(
        select(Car).filter(Car.id == car_id, Car.driver_id == current_driver.id)
    )
    car = result.scalars().first()
    
    if not car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Car with ID {car_id} not found"
        )
    
    # Check if license plate is being updated and already exists
    if car_update.license_plate and car_update.license_plate != car.license_plate:
        result = await db.execute(select(Car).filter(Car.license_plate == car_update.license_plate))
        if result.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="License plate already registered"
            )
    
    # Update car fields
    for field, value in car_update.dict(exclude_unset=True).items():
        setattr(car, field, value)
    
    await db.commit()
    await db.refresh(car)
    
    return CarDetailResponse(data=car)


@router.delete("/{car_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_car(
    car_id: int,
    db: AsyncSession = Depends(get_db),
    current_driver = Depends(get_current_driver)
):
    """Delete a specific car by ID"""
    result = await db.execute(
        select(Car).filter(Car.id == car_id, Car.driver_id == current_driver.id)
    )
    car = result.scalars().first()
    
    if not car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Car with ID {car_id} not found"
        )
    
    # Check if car is used in any active rides
    # This would require a query to the rides table
    # For now, we'll just set is_active to False instead of deleting
    car.is_active = False
    await db.commit()
    
    return None 
