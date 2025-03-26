import pytest
from typing import Generator, Dict
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.db.session import SessionLocal
from app.core.config import settings
from app.core.security import create_access_token
from app.models.user import User
from app.models.ride import Ride
from app.models.location import Location
from app.models.ride_stop import RideStop
from app.models.recurring_pattern import RecurringPattern

@pytest.fixture(scope="session")
def db() -> Generator:
    yield SessionLocal()

@pytest.fixture(scope="module")
def client() -> Generator:
    with TestClient(app) as c:
        yield c

@pytest.fixture(scope="module")
def test_user(db: Session) -> Dict[str, str]:
    user = User(
        email="test@example.com",
        hashed_password="hashed_password",
        full_name="Test User",
        phone_number="1234567890",
        is_active=True,
        is_verified=True,
        role="rider"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {
        "id": str(user.id),
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role
    }

@pytest.fixture(scope="module")
def test_driver(db: Session) -> Dict[str, str]:
    driver = User(
        email="driver@example.com",
        hashed_password="hashed_password",
        full_name="Test Driver",
        phone_number="0987654321",
        is_active=True,
        is_verified=True,
        role="driver",
        driver_verified=True
    )
    db.add(driver)
    db.commit()
    db.refresh(driver)
    return {
        "id": str(driver.id),
        "email": driver.email,
        "full_name": driver.full_name,
        "role": driver.role
    }

@pytest.fixture(scope="module")
def test_admin(db: Session) -> Dict[str, str]:
    admin = User(
        email="admin@example.com",
        hashed_password="hashed_password",
        full_name="Test Admin",
        phone_number="5555555555",
        is_active=True,
        is_verified=True,
        role="admin"
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return {
        "id": str(admin.id),
        "email": admin.email,
        "full_name": admin.full_name,
        "role": admin.role
    }

@pytest.fixture(scope="module")
def test_location(db: Session) -> Dict[str, str]:
    location = Location(
        latitude=37.7749,
        longitude=-122.4194,
        formatted_address="123 Test St, San Francisco, CA 94105"
    )
    db.add(location)
    db.commit()
    db.refresh(location)
    return {
        "id": str(location.id),
        "latitude": location.latitude,
        "longitude": location.longitude,
        "formatted_address": location.formatted_address
    }

@pytest.fixture(scope="module")
def test_ride(db: Session, test_user: Dict[str, str], test_location: Dict[str, str]) -> Dict[str, str]:
    ride = Ride(
        rider_id=test_user["id"],
        start_location_id=test_location["id"],
        end_location_id=test_location["id"],
        status="pending",
        distance_miles=10.0,
        duration_minutes=20,
        price=50.0,
        platform_fee=7.5,
        driver_earnings=42.5,
        number_of_stops=1,
        is_recurring=False,
        notes="Test ride"
    )
    db.add(ride)
    db.commit()
    db.refresh(ride)
    return {
        "id": str(ride.id),
        "rider_id": ride.rider_id,
        "status": ride.status,
        "price": ride.price
    }

@pytest.fixture(scope="module")
def test_ride_stop(db: Session, test_ride: Dict[str, str], test_location: Dict[str, str]) -> Dict[str, str]:
    stop = RideStop(
        ride_id=test_ride["id"],
        location_id=test_location["id"],
        stop_order=1,
        estimated_arrival_time=30
    )
    db.add(stop)
    db.commit()
    db.refresh(stop)
    return {
        "id": str(stop.id),
        "ride_id": stop.ride_id,
        "location_id": stop.location_id,
        "stop_order": stop.stop_order
    }

@pytest.fixture(scope="module")
def test_recurring_pattern(db: Session, test_ride: Dict[str, str]) -> Dict[str, str]:
    pattern = RecurringPattern(
        ride_id=test_ride["id"],
        frequency="weekly",
        days_of_week=["monday", "wednesday", "friday"],
        start_time="09:00",
        end_time="17:00",
        start_date="2024-01-01",
        end_date="2024-12-31"
    )
    db.add(pattern)
    db.commit()
    db.refresh(pattern)
    return {
        "id": str(pattern.id),
        "ride_id": pattern.ride_id,
        "frequency": pattern.frequency,
        "days_of_week": pattern.days_of_week
    }

@pytest.fixture(scope="module")
def test_user_token(test_user: Dict[str, str]) -> str:
    return create_access_token(test_user["id"])

@pytest.fixture(scope="module")
def test_driver_token(test_driver: Dict[str, str]) -> str:
    return create_access_token(test_driver["id"])

@pytest.fixture(scope="module")
def test_admin_token(test_admin: Dict[str, str]) -> str:
    return create_access_token(test_admin["id"]) 
