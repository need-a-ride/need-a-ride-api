from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Dict, Any, Optional

from app.database.session import get_db
from app.models.user import Customer, Driver
from app.schemas.user import UserResponse
from app.schemas.response import (
    UserProfileResponse,
    GetRideResponse,
    RideListResponse,
    RideListResponseData
)
from app.schemas.requests import (
    UpdateUserProfileRequest,
    ChangePasswordRequest,
    UpdateDriverLicenseRequest
)
from app.services.auth_service import get_current_user, get_current_driver
from app.services.ride_service import get_rides, get_total_rides_count

router = APIRouter()


@router.get("/me", response_model=UserProfileResponse)
async def get_current_user_profile(
    current_user = Depends(get_current_user)
):
    """Get the current user's profile information"""
    if isinstance(current_user, Driver):
        return UserProfileResponse(
            id=current_user.id,
            email=current_user.email,
            name=current_user.name,
            phone=current_user.phone,
            profile_picture=current_user.profile_picture,
            user_type="driver",
            is_verified=current_user.is_verified,
            license_number=current_user.license_number,
            license_expiry=current_user.license_expiry
        )
    else:
        return UserProfileResponse(
            id=current_user.id,
            email=current_user.email,
            name=current_user.name,
            phone=current_user.phone,
            profile_picture=current_user.profile_picture,
            user_type="customer"
        )


@router.put("/me", response_model=UserProfileResponse)
async def update_user_profile(
    profile_data: UpdateUserProfileRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update the current user's profile information"""
    # Update user fields if provided
    if profile_data.name:
        current_user.name = profile_data.name
    if profile_data.phone:
        current_user.phone = profile_data.phone
    if profile_data.email:
        # Check if email is already taken
        if profile_data.email != current_user.email:
            # Check in both customer and driver tables
            customer_result = await db.execute(
                select(Customer).filter(Customer.email == profile_data.email)
            )
            driver_result = await db.execute(
                select(Driver).filter(Driver.email == profile_data.email)
            )
            
            if customer_result.scalars().first() or driver_result.scalars().first():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already in use"
                )
        current_user.email = profile_data.email
    
    await db.commit()
    await db.refresh(current_user)
    
    # Return the updated profile
    if isinstance(current_user, Driver):
        return UserProfileResponse(
            id=current_user.id,
            email=current_user.email,
            name=current_user.name,
            phone=current_user.phone,
            profile_picture=current_user.profile_picture,
            user_type="driver",
            is_verified=current_user.is_verified,
            license_number=current_user.license_number,
            license_expiry=current_user.license_expiry
        )
    else:
        return UserProfileResponse(
            id=current_user.id,
            email=current_user.email,
            name=current_user.name,
            phone=current_user.phone,
            profile_picture=current_user.profile_picture,
            user_type="customer"
        )


@router.put("/me/license", response_model=UserProfileResponse)
async def update_driver_license(
    license_data: UpdateDriverLicenseRequest,
    db: AsyncSession = Depends(get_db),
    current_driver: Driver = Depends(get_current_driver)
):
    """Update the current driver's license information"""
    current_driver.license_number = license_data.license_number
    current_driver.license_expiry = license_data.license_expiry
    
    # Set is_verified to False since the license info has been updated
    # and needs to be verified again
    current_driver.is_verified = False
    
    await db.commit()
    await db.refresh(current_driver)
    
    return UserProfileResponse(
        id=current_driver.id,
        email=current_driver.email,
        name=current_driver.name,
        phone=current_driver.phone,
        profile_picture=current_driver.profile_picture,
        user_type="driver",
        is_verified=current_driver.is_verified,
        license_number=current_driver.license_number,
        license_expiry=current_driver.license_expiry
    )


@router.post("/me/change-password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    password_data: ChangePasswordRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Change the current user's password"""
    # This is a placeholder - you'll need to implement the actual password change logic
    # Verify current password
    # if not verify_password(password_data.current_password, current_user.password_hash):
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="Current password is incorrect"
    #     )
    
    # Check if new password and confirm password match
    if password_data.new_password != password_data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password and confirm password do not match"
        )
    
    # Update password
    # current_user.password_hash = get_password_hash(password_data.new_password)
    # await db.commit()
    
    return None


@router.get("/me/rides", response_model=RideListResponse)
async def get_user_rides(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    upcoming_only: bool = Query(False, description="Only show upcoming rides"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get rides associated with the current user"""
    # For drivers, get rides they're driving
    # For customers, get rides they're participating in
    # This is a simplified example - you'd need to implement the actual service function
    
    # For now, just return all rides (you should implement proper filtering)
    rides = await get_rides(
        db, 
        skip=(page - 1) * per_page, 
        limit=per_page,
        driver_id=current_user.id if isinstance(current_user, Driver) else None,
        upcoming_only=upcoming_only
    )
    total_count = await get_total_rides_count(
        db,
        driver_id=current_user.id if isinstance(current_user, Driver) else None,
        upcoming_only=upcoming_only
    )
    total_pages = (total_count + per_page - 1) // per_page  # Ceiling division
    
    ride_list_data = RideListResponseData(
        items=rides,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
        total_items=total_count
    )
    
    return RideListResponse(data=ride_list_data)


@router.get("/{user_id}", response_model=UserProfileResponse)
async def get_user_profile(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a user's profile by ID"""
    # Try to find user in customers
    result = await db.execute(select(Customer).filter(Customer.id == user_id))
    user = result.scalars().first()
    
    if not user:
        # Try to find user in drivers
        result = await db.execute(select(Driver).filter(Driver.id == user_id))
        user = result.scalars().first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    if isinstance(user, Driver):
        return UserProfileResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            phone=user.phone,
            profile_picture=user.profile_picture,
            user_type="driver",
            is_verified=user.is_verified,
            license_number=user.license_number,
            license_expiry=user.license_expiry
        )
    else:
        return UserProfileResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            phone=user.phone,
            profile_picture=user.profile_picture,
            user_type="customer"
        )
