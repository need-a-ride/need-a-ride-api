import pytest
from datetime import timedelta
from app.core.security import (
    create_access_token,
    verify_password,
    get_password_hash,
    generate_verification_code,
    verify_token,
    create_password_reset_token,
    verify_password_reset_token,
    create_email_verification_token,
    verify_email_verification_token,
    create_phone_verification_token,
    verify_phone_verification_token
)

def test_password_hash():
    """Test password hashing and verification"""
    password = "test_password"
    hashed_password = get_password_hash(password)
    assert verify_password(password, hashed_password) is True
    assert verify_password("wrong_password", hashed_password) is False

def test_access_token():
    """Test access token creation and verification"""
    user_id = "123"
    token = create_access_token(user_id)
    assert verify_token(token) == user_id
    assert verify_token("invalid_token") is None

def test_access_token_with_expiry():
    """Test access token creation with custom expiry"""
    user_id = "123"
    expires_delta = timedelta(minutes=30)
    token = create_access_token(user_id, expires_delta)
    assert verify_token(token) == user_id

def test_verification_code():
    """Test verification code generation"""
    code = generate_verification_code()
    assert len(code) == 6
    assert code.isdigit()

def test_password_reset_token():
    """Test password reset token creation and verification"""
    email = "test@example.com"
    token = create_password_reset_token(email)
    assert verify_password_reset_token(token) == email
    assert verify_password_reset_token("invalid_token") is None

def test_email_verification_token():
    """Test email verification token creation and verification"""
    email = "test@example.com"
    token = create_email_verification_token(email)
    assert verify_email_verification_token(token) == email
    assert verify_email_verification_token("invalid_token") is None

def test_phone_verification_token():
    """Test phone verification token creation and verification"""
    phone = "1234567890"
    token = create_phone_verification_token(phone)
    assert verify_phone_verification_token(token) == phone
    assert verify_phone_verification_token("invalid_token") is None

def test_token_expiry():
    """Test that tokens expire properly"""
    # Create a token with very short expiry
    token = create_access_token("123", timedelta(seconds=1))
    import time
    time.sleep(2)  # Wait for token to expire
    assert verify_token(token) is None

def test_token_type_verification():
    """Test that token type verification works correctly"""
    # Create a password reset token
    email = "test@example.com"
    token = create_password_reset_token(email)
    
    # Try to verify it as an email verification token
    assert verify_email_verification_token(token) is None
    
    # Try to verify it as a phone verification token
    assert verify_phone_verification_token(token) is None

def test_invalid_token_format():
    """Test handling of invalid token formats"""
    assert verify_token("invalid.token.format") is None
    assert verify_password_reset_token("invalid.token.format") is None
    assert verify_email_verification_token("invalid.token.format") is None
    assert verify_phone_verification_token("invalid.token.format") is None 
