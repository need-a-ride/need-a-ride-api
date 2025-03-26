from typing import Dict, Any
from app.core.config import settings

# API Settings
API_V1_STR = settings.API_V1_STR
PROJECT_NAME = settings.PROJECT_NAME

# Database Settings
DATABASE_URL = settings.SQLALCHEMY_DATABASE_URI

# Security Settings
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

# Google OAuth Settings
GOOGLE_CLIENT_ID = settings.GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET = settings.GOOGLE_CLIENT_SECRET
GOOGLE_REDIRECT_URI = settings.GOOGLE_REDIRECT_URI

# Google Maps Settings
GOOGLE_MAPS_API_KEY = settings.GOOGLE_MAPS_API_KEY

# Stripe Settings
STRIPE_SECRET_KEY = settings.STRIPE_SECRET_KEY
STRIPE_WEBHOOK_SECRET = settings.STRIPE_WEBHOOK_SECRET

# Email Settings
SMTP_TLS = settings.SMTP_TLS
SMTP_PORT = settings.SMTP_PORT
SMTP_HOST = settings.SMTP_HOST
SMTP_USER = settings.SMTP_USER
SMTP_PASSWORD = settings.SMTP_PASSWORD
EMAILS_FROM_EMAIL = settings.EMAILS_FROM_EMAIL
EMAILS_FROM_NAME = settings.EMAILS_FROM_NAME

# Redis Settings
REDIS_HOST = settings.REDIS_HOST
REDIS_PORT = settings.REDIS_PORT

# Rate Limiting Settings
RATE_LIMIT_PER_MINUTE = settings.RATE_LIMIT_PER_MINUTE

# Ride Settings
MIN_RIDE_PRICE = settings.MIN_RIDE_PRICE
MAX_RIDE_PRICE = settings.MAX_RIDE_PRICE
PLATFORM_FEE_PERCENTAGE = settings.PLATFORM_FEE_PERCENTAGE
DRIVER_MIN_EARNINGS_PERCENTAGE = settings.DRIVER_MIN_EARNINGS_PERCENTAGE

# CORS Settings
BACKEND_CORS_ORIGINS = settings.BACKEND_CORS_ORIGINS

# Application Constants
class AppConstants:
    # User Roles
    ROLE_ADMIN = "admin"
    ROLE_DRIVER = "driver"
    ROLE_RIDER = "rider"
    
    # Ride Status
    RIDE_STATUS_PENDING = "pending"
    RIDE_STATUS_ACCEPTED = "accepted"
    RIDE_STATUS_IN_PROGRESS = "in_progress"
    RIDE_STATUS_COMPLETED = "completed"
    RIDE_STATUS_CANCELLED = "cancelled"
    
    # Payment Status
    PAYMENT_STATUS_PENDING = "pending"
    PAYMENT_STATUS_COMPLETED = "completed"
    PAYMENT_STATUS_FAILED = "failed"
    PAYMENT_STATUS_REFUNDED = "refunded"
    
    # Verification Types
    VERIFICATION_TYPE_EMAIL = "email"
    VERIFICATION_TYPE_PHONE = "phone"
    VERIFICATION_TYPE_DRIVER = "driver"
    
    # File Types
    ALLOWED_FILE_TYPES = ["image/jpeg", "image/png", "image/jpg"]
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    
    # Pagination
    DEFAULT_PAGE_SIZE = 10
    MAX_PAGE_SIZE = 100
    
    # Cache Keys
    CACHE_KEY_USER = "user:{}"
    CACHE_KEY_RIDE = "ride:{}"
    CACHE_KEY_LOCATION = "location:{}"
    
    # Rate Limiting Keys
    RATE_LIMIT_KEY = "rate_limit:{}"
    
    # Error Messages
    ERROR_MESSAGES = {
        "invalid_credentials": "Invalid email or password",
        "user_not_found": "User not found",
        "ride_not_found": "Ride not found",
        "unauthorized": "Not authorized to perform this action",
        "invalid_token": "Invalid or expired token",
        "email_not_verified": "Email not verified",
        "phone_not_verified": "Phone number not verified",
        "driver_not_verified": "Driver not verified",
        "ride_full": "Ride is full",
        "ride_closed": "Ride registration is closed",
        "invalid_payment": "Invalid payment information",
        "payment_failed": "Payment failed",
        "invalid_location": "Invalid location information",
        "route_not_found": "Could not calculate route",
        "invalid_file": "Invalid file type or size",
    }
    
    # Success Messages
    SUCCESS_MESSAGES = {
        "user_created": "User created successfully",
        "user_updated": "User updated successfully",
        "ride_created": "Ride created successfully",
        "ride_updated": "Ride updated successfully",
        "ride_accepted": "Ride accepted successfully",
        "ride_completed": "Ride completed successfully",
        "payment_success": "Payment processed successfully",
        "email_sent": "Email sent successfully",
        "verification_sent": "Verification code sent successfully",
        "verification_complete": "Verification completed successfully",
    }
    
    # Validation Rules
    VALIDATION_RULES = {
        "password_min_length": 8,
        "password_max_length": 50,
        "name_min_length": 2,
        "name_max_length": 50,
        "phone_length": 10,
        "email_max_length": 255,
        "address_max_length": 255,
        "notes_max_length": 500,
        "ride_max_stops": 5,
        "ride_max_riders": 8,
    }
    
    # Time Constants
    TIME_CONSTANTS = {
        "verification_code_expiry": 10,  # minutes
        "password_reset_expiry": 24,     # hours
        "email_verification_expiry": 24,  # hours
        "token_expiry": 8,               # days
        "cache_expiry": 3600,            # seconds (1 hour)
    } 
