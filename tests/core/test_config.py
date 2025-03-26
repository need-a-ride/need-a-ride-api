import pytest
from app.core.config import settings

def test_settings_initialization():
    """Test that settings are properly initialized"""
    assert settings.API_V1_STR == "/api/v1"
    assert settings.PROJECT_NAME == "NeedARide API"
    assert settings.ALGORITHM == "HS256"
    assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 60 * 24 * 8  # 8 days
    assert settings.SMTP_TLS is True
    assert settings.SMTP_PORT == 587
    assert settings.MIN_RIDE_PRICE == 5.0
    assert settings.MAX_RIDE_PRICE == 1000.0
    assert settings.PLATFORM_FEE_PERCENTAGE == 0.15
    assert settings.DRIVER_MIN_EARNINGS_PERCENTAGE == 0.70

def test_database_uri():
    """Test that database URI is properly constructed"""
    expected_uri = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}/{settings.POSTGRES_DB}"
    assert settings.SQLALCHEMY_DATABASE_URI == expected_uri

def test_cors_origins():
    """Test CORS origins configuration"""
    assert isinstance(settings.BACKEND_CORS_ORIGINS, list)

def test_environment_variables():
    """Test that environment variables are properly loaded"""
    # These should be empty strings if not set in environment
    assert isinstance(settings.GOOGLE_CLIENT_ID, str)
    assert isinstance(settings.GOOGLE_CLIENT_SECRET, str)
    assert isinstance(settings.GOOGLE_MAPS_API_KEY, str)
    assert isinstance(settings.STRIPE_SECRET_KEY, str)
    assert isinstance(settings.STRIPE_WEBHOOK_SECRET, str)
    assert isinstance(settings.SMTP_HOST, str)
    assert isinstance(settings.SMTP_USER, str)
    assert isinstance(settings.SMTP_PASSWORD, str)
    assert isinstance(settings.EMAILS_FROM_EMAIL, str)
    assert isinstance(settings.REDIS_HOST, str)
    assert isinstance(settings.REDIS_PORT, int)

def test_redis_port():
    """Test that Redis port is properly converted to integer"""
    assert isinstance(settings.REDIS_PORT, int)

def test_secret_key():
    """Test that secret key is properly set"""
    assert isinstance(settings.SECRET_KEY, str)
    assert len(settings.SECRET_KEY) > 0

def test_google_redirect_uri():
    """Test Google OAuth redirect URI"""
    assert settings.GOOGLE_REDIRECT_URI == "http://localhost:8000/api/v1/auth/google/callback"

def test_rate_limit():
    """Test rate limiting configuration"""
    assert isinstance(settings.RATE_LIMIT_PER_MINUTE, int)
    assert settings.RATE_LIMIT_PER_MINUTE == 60 
