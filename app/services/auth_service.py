import os

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from passlib.context import CryptContext
from jose import JWTError, jwt
from app.models.user import Customer, Driver
from app.schemas.requests import UserRegisterRequest, UserType
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status, Cookie, Request
from fastapi.security import OAuth2PasswordBearer
from app.database.session import get_db
from typing import Optional, Dict, Any, Union

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES") or 30)
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS") or 7)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

# Token types
ACCESS_TOKEN = "access_token"
REFRESH_TOKEN = "refresh_token"

# Cookie settings
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "True").lower() in ("true", "1", "t")
COOKIE_HTTPONLY = True
COOKIE_SAMESITE = "lax"


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


async def create_user(db: AsyncSession, user: UserRegisterRequest):
    hashed_password = get_password_hash(user.password)
    
    if user.user_type == UserType.DRIVER:
        # Create a driver (license fields are optional)
        db_user = Driver(
            name=user.name,
            email=user.email,
            phone=user.phone,
            password_hash=hashed_password,
            license_number=user.license_number,
            license_expiry=user.license_expiry
        )
    else:
        # Create a customer
        db_user = Customer(
            name=user.name,
            email=user.email,
            phone=user.phone,
            password_hash=hashed_password,
        )
    
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def authenticate_user(db: AsyncSession, email: str, password: str):
    # Try to find user in customers
    result = await db.execute(select(Customer).filter(Customer.email == email))
    user = result.scalars().first()
    
    if not user:
        # Try to find user in drivers
        result = await db.execute(select(Driver).filter(Driver.email == email))
        user = result.scalars().first()
    
    if user and verify_password(password, user.password_hash):
        return user
    return None


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[Union[Customer, Driver]]:
    """Get a user by email from either customers or drivers table"""
    # Try to find user in customers
    result = await db.execute(select(Customer).filter(Customer.email == email))
    user = result.scalars().first()
    
    if not user:
        # Try to find user in drivers
        result = await db.execute(select(Driver).filter(Driver.email == email))
        user = result.scalars().first()
        
    return user


def create_token(data: dict, token_type: str, expires_delta: timedelta = None):
    to_encode = data.copy()
    
    if token_type == ACCESS_TOKEN:
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    else:  # REFRESH_TOKEN
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({"exp": expire, "type": token_type})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_access_token(data: dict, expires_delta: timedelta = None):
    return create_token(data, ACCESS_TOKEN, expires_delta)


def create_refresh_token(data: dict, expires_delta: timedelta = None):
    return create_token(data, REFRESH_TOKEN, expires_delta)


def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


async def get_current_user_from_token(db: AsyncSession, token: str):
    if not token:
        return None
        
    payload = decode_token(token)
    if not payload or payload.get("type") != ACCESS_TOKEN:
        return None
        
    email = payload.get("sub")
    if not email:
        return None
    
    return await get_user_by_email(db, email)


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db), 
    token: str = Depends(oauth2_scheme),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # First try to get token from Authorization header
    user = await get_current_user_from_token(db, token)
    
    # If not found, try to get from cookies
    if not user:
        access_token = request.cookies.get("access_token")
        user = await get_current_user_from_token(db, access_token)
    
    if not user:
        raise credentials_exception
        
    return user


async def get_current_driver(
    request: Request,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    user = await get_current_user(request, db, token)
    
    if not isinstance(user, Driver):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a driver"
        )
    
    return user


async def get_current_customer(
    request: Request,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    user = await get_current_user(request, db, token)
    
    if not isinstance(user, Customer):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a customer"
        )
    
    return user


async def get_user_from_refresh_token(db: AsyncSession, refresh_token: str):
    if not refresh_token:
        return None
        
    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != REFRESH_TOKEN:
        return None
        
    email = payload.get("sub")
    if not email:
        return None
    
    return await get_user_by_email(db, email)
