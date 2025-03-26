import pytest
from app.core.settings import AppConstants

def test_user_roles():
    """Test user role constants"""
    assert AppConstants.ROLE_ADMIN == "admin"
    assert AppConstants.ROLE_DRIVER == "driver"
    assert AppConstants.ROLE_RIDER == "rider"

def test_ride_status():
    """Test ride status constants"""
    assert AppConstants.RIDE_STATUS_PENDING == "pending"
    assert AppConstants.RIDE_STATUS_ACCEPTED == "accepted"
    assert AppConstants.RIDE_STATUS_IN_PROGRESS == "in_progress"
    assert AppConstants.RIDE_STATUS_COMPLETED == "completed"
    assert AppConstants.RIDE_STATUS_CANCELLED == "cancelled"

def test_payment_status():
    """Test payment status constants"""
    assert AppConstants.PAYMENT_STATUS_PENDING == "pending"
    assert AppConstants.PAYMENT_STATUS_COMPLETED == "completed"
    assert AppConstants.PAYMENT_STATUS_FAILED == "failed"
    assert AppConstants.PAYMENT_STATUS_REFUNDED == "refunded"

def test_verification_types():
    """Test verification type constants"""
    assert AppConstants.VERIFICATION_TYPE_EMAIL == "email"
    assert AppConstants.VERIFICATION_TYPE_PHONE == "phone"
    assert AppConstants.VERIFICATION_TYPE_DRIVER == "driver"

def test_file_types():
    """Test allowed file types"""
    assert "image/jpeg" in AppConstants.ALLOWED_FILE_TYPES
    assert "image/png" in AppConstants.ALLOWED_FILE_TYPES
    assert "image/jpg" in AppConstants.ALLOWED_FILE_TYPES
    assert AppConstants.MAX_FILE_SIZE == 5 * 1024 * 1024  # 5MB

def test_pagination():
    """Test pagination constants"""
    assert AppConstants.DEFAULT_PAGE_SIZE == 10
    assert AppConstants.MAX_PAGE_SIZE == 100

def test_cache_keys():
    """Test cache key formats"""
    assert AppConstants.CACHE_KEY_USER == "user:{}"
    assert AppConstants.CACHE_KEY_RIDE == "ride:{}"
    assert AppConstants.CACHE_KEY_LOCATION == "location:{}"

def test_rate_limit_key():
    """Test rate limit key format"""
    assert AppConstants.RATE_LIMIT_KEY == "rate_limit:{}"

def test_error_messages():
    """Test error message constants"""
    assert "invalid_credentials" in AppConstants.ERROR_MESSAGES
    assert "user_not_found" in AppConstants.ERROR_MESSAGES
    assert "ride_not_found" in AppConstants.ERROR_MESSAGES
    assert "unauthorized" in AppConstants.ERROR_MESSAGES
    assert "invalid_token" in AppConstants.ERROR_MESSAGES
    assert "email_not_verified" in AppConstants.ERROR_MESSAGES
    assert "phone_not_verified" in AppConstants.ERROR_MESSAGES
    assert "driver_not_verified" in AppConstants.ERROR_MESSAGES
    assert "ride_full" in AppConstants.ERROR_MESSAGES
    assert "ride_closed" in AppConstants.ERROR_MESSAGES
    assert "invalid_payment" in AppConstants.ERROR_MESSAGES
    assert "payment_failed" in AppConstants.ERROR_MESSAGES
    assert "invalid_location" in AppConstants.ERROR_MESSAGES
    assert "route_not_found" in AppConstants.ERROR_MESSAGES
    assert "invalid_file" in AppConstants.ERROR_MESSAGES

def test_success_messages():
    """Test success message constants"""
    assert "user_created" in AppConstants.SUCCESS_MESSAGES
    assert "user_updated" in AppConstants.SUCCESS_MESSAGES
    assert "ride_created" in AppConstants.SUCCESS_MESSAGES
    assert "ride_updated" in AppConstants.SUCCESS_MESSAGES
    assert "ride_accepted" in AppConstants.SUCCESS_MESSAGES
    assert "ride_completed" in AppConstants.SUCCESS_MESSAGES
    assert "payment_success" in AppConstants.SUCCESS_MESSAGES
    assert "email_sent" in AppConstants.SUCCESS_MESSAGES
    assert "verification_sent" in AppConstants.SUCCESS_MESSAGES
    assert "verification_complete" in AppConstants.SUCCESS_MESSAGES

def test_validation_rules():
    """Test validation rule constants"""
    assert AppConstants.VALIDATION_RULES["password_min_length"] == 8
    assert AppConstants.VALIDATION_RULES["password_max_length"] == 50
    assert AppConstants.VALIDATION_RULES["name_min_length"] == 2
    assert AppConstants.VALIDATION_RULES["name_max_length"] == 50
    assert AppConstants.VALIDATION_RULES["phone_length"] == 10
    assert AppConstants.VALIDATION_RULES["email_max_length"] == 255
    assert AppConstants.VALIDATION_RULES["address_max_length"] == 255
    assert AppConstants.VALIDATION_RULES["notes_max_length"] == 500
    assert AppConstants.VALIDATION_RULES["ride_max_stops"] == 5
    assert AppConstants.VALIDATION_RULES["ride_max_riders"] == 8

def test_time_constants():
    """Test time constant values"""
    assert AppConstants.TIME_CONSTANTS["verification_code_expiry"] == 10  # minutes
    assert AppConstants.TIME_CONSTANTS["password_reset_expiry"] == 24    # hours
    assert AppConstants.TIME_CONSTANTS["email_verification_expiry"] == 24  # hours
    assert AppConstants.TIME_CONSTANTS["token_expiry"] == 8              # days
    assert AppConstants.TIME_CONSTANTS["cache_expiry"] == 3600           # seconds (1 hour) 
