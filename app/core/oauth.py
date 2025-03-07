import os
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2AuthorizationCodeBearer
from authlib.integrations.starlette_client import OAuth, OAuthError
from starlette.requests import Request
from starlette.responses import RedirectResponse
from app.models.user import Customer
from app.database.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional, Dict, Any

# Load OAuth configuration from environment variables
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/v1/auth/google/callback")

# Initialize OAuth
oauth = OAuth()
oauth.register(
    name="google",
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={
        "scope": "openid email profile",
        "redirect_uri": GOOGLE_REDIRECT_URI,
    },
)

# Cookie settings
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "True").lower() in ("true", "1", "t")
COOKIE_HTTPONLY = True
COOKIE_SAMESITE = "lax"
SESSION_COOKIE_NAME = "session_token"
SESSION_EXPIRE_DAYS = int(os.getenv("SESSION_EXPIRE_DAYS", "7"))


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[Customer]:
    """Get a user by email"""
    result = await db.execute(select(Customer).filter(Customer.email == email))
    return result.scalars().first()


async def create_or_update_user(db: AsyncSession, user_info: Dict[str, Any]) -> Customer:
    """Create or update a user from Google profile information"""
    email = user_info.get("email")
    if not email:
        raise ValueError("Email not provided by Google")
    
    # Check if user exists
    user = await get_user_by_email(db, email)
    
    if user:
        # Update existing user
        user.name = user_info.get("name", user.name)
        user.google_id = user_info.get("sub", user.google_id)
        user.profile_picture = user_info.get("picture", user.profile_picture)
        await db.commit()
        await db.refresh(user)
        return user
    else:
        # Create new user
        new_user = Customer(
            email=email,
            name=user_info.get("name", ""),
            google_id=user_info.get("sub"),
            profile_picture=user_info.get("picture"),
            # Set a default phone number (you might want to ask for this later)
            phone="",
        )
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return new_user


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> Customer:
    """Get the current user from session cookie"""
    session_token = request.cookies.get(SESSION_COOKIE_NAME)
    
    if not session_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # In a real application, you would validate the session token
    # For now, we'll assume it contains the user's email
    try:
        user = await get_user_by_email(db, session_token)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) 
