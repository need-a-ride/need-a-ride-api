import os
from datetime import timedelta, datetime

from fastapi import APIRouter, HTTPException, Depends, Response, Request, Cookie, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional, Dict, Any
from starlette.responses import RedirectResponse

from app.models.user import Customer, Driver
from app.database.session import get_db
from app.schemas.user import UserResponse
from app.schemas.response import (
    LoginResponse, 
    RegisterResponse, 
    RefreshTokenResponse, 
    LogoutResponse,
    UserProfileResponse,
    LoginResponseData,
    RegisterResponseData,
    RefreshTokenResponseData,
    LogoutResponseData,
    ErrorResponseData
)
from app.schemas.requests import (
    RefreshTokenRequest,
    UserLoginRequest,
    UserRegisterRequest,
    UserType
)
from app.services.auth_service import (
    create_user,
    authenticate_user,
    create_access_token,
    create_refresh_token,
    get_user_from_refresh_token,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
    COOKIE_SECURE,
    COOKIE_HTTPONLY,
    COOKIE_SAMESITE
)

router = APIRouter()


@router.post("/register/", response_model=RegisterResponse)
async def register_user(
    user: UserRegisterRequest, 
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    # Check if user already exists in either customers or drivers table
    existing_customer = await db.execute(
        select(Customer).filter(Customer.email == user.email)
    )
    existing_driver = await db.execute(
        select(Driver).filter(Driver.email == user.email)
    )
    
    if existing_customer.scalars().first() or existing_driver.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    new_user = await create_user(db, user)
    
    # Generate tokens
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    access_token = create_access_token(
        data={"sub": new_user.email}, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(
        data={"sub": new_user.email}, expires_delta=refresh_token_expires
    )
    
    # Set cookies
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=COOKIE_HTTPONLY,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=COOKIE_HTTPONLY,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )
    
    # Create response data based on user type
    if user.user_type == UserType.DRIVER:
        user_profile = UserProfileResponse(
            id=new_user.id,
            email=new_user.email,
            name=new_user.name,
            phone=new_user.phone,
            profile_picture=new_user.profile_picture,
            user_type="driver",
            is_verified=new_user.is_verified,
            license_number=new_user.license_number,
            license_expiry=new_user.license_expiry
        )
    else:
        user_profile = UserProfileResponse(
            id=new_user.id,
            email=new_user.email,
            name=new_user.name,
            phone=new_user.phone,
            profile_picture=new_user.profile_picture,
            user_type="customer"
        )
    
    register_data = RegisterResponseData(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=user_profile
    )
    
    return RegisterResponse(data=register_data)


@router.post("/login/", response_model=LoginResponse)
async def login_user(
    user: UserLoginRequest, 
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    # Authenticate user
    authenticated_user = await authenticate_user(db, user.email, user.password)
    if not authenticated_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    # Generate tokens
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    access_token = create_access_token(
        data={"sub": authenticated_user.email}, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(
        data={"sub": authenticated_user.email}, expires_delta=refresh_token_expires
    )
    
    # Set cookies
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=COOKIE_HTTPONLY,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=COOKIE_HTTPONLY,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )
    
    # Create response data based on user type
    if isinstance(authenticated_user, Driver):
        user_profile = UserProfileResponse(
            id=authenticated_user.id,
            email=authenticated_user.email,
            name=authenticated_user.name,
            phone=authenticated_user.phone,
            profile_picture=authenticated_user.profile_picture,
            user_type="driver",
            is_verified=authenticated_user.is_verified,
            license_number=authenticated_user.license_number,
            license_expiry=authenticated_user.license_expiry
        )
    else:
        user_profile = UserProfileResponse(
            id=authenticated_user.id,
            email=authenticated_user.email,
            name=authenticated_user.name,
            phone=authenticated_user.phone,
            profile_picture=authenticated_user.profile_picture,
            user_type="customer"
        )
    
    login_data = LoginResponseData(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=user_profile
    )
    
    return LoginResponse(data=login_data)


@router.post("/refresh/", response_model=RefreshTokenResponse)
async def refresh_token_endpoint(
    response: Response,
    request: Request,
    refresh_token_cookie: Optional[str] = Cookie(None, alias="refresh_token"),
    refresh_token_body: Optional[RefreshTokenRequest] = None,
    db: AsyncSession = Depends(get_db)
):
    # First try to get token from cookie
    refresh_token = refresh_token_cookie
    
    # If not in cookie, try to get from request body
    if not refresh_token and refresh_token_body and refresh_token_body.refresh_token:
        refresh_token = refresh_token_body.refresh_token
    
    # If still not found, try to parse JSON body manually
    if not refresh_token:
        try:
            body_data = await request.json()
            refresh_token = body_data.get("refresh_token")
        except:
            # If JSON parsing fails, try form data
            try:
                form_data = await request.form()
                refresh_token = form_data.get("refresh_token")
            except:
                pass
    
    # If token is still not found, return error
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token missing",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Validate the token
    user = await get_user_from_refresh_token(db, refresh_token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Generate new tokens
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    new_refresh_token = create_refresh_token(
        data={"sub": user.email}, expires_delta=refresh_token_expires
    )
    
    # Set cookies
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=COOKIE_HTTPONLY,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=COOKIE_HTTPONLY,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )
    
    # Create response data
    refresh_data = RefreshTokenResponseData(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    
    return RefreshTokenResponse(data=refresh_data)


@router.get("/me", response_model=UserProfileResponse)
async def get_current_user_profile(current_user = Depends(get_current_user)):
    """Get the current user's profile"""
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


@router.post("/logout/", response_model=LogoutResponse)
async def logout(response: Response):
    """Logout the current user by clearing the session cookie"""
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")
    
    # Create response data
    logout_data = LogoutResponseData(message="Successfully logged out")
    
    return LogoutResponse(data=logout_data)


# OAuth routes for future implementation
@router.get("/oauth/google/login", status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def login_via_google():
    """
    Placeholder for Google OAuth login
    This will be implemented in the mobile app
    """
    return {"message": "Google OAuth login will be implemented in the mobile app"}


@router.get("/oauth/google/callback", status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def google_auth_callback():
    """
    Placeholder for Google OAuth callback
    This will be implemented in the mobile app
    """
    return {"message": "Google OAuth callback will be implemented in the mobile app"}
