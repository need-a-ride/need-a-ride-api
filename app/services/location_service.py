from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timedelta
from app.models.ride import Location
from typing import Optional, Tuple


class LocationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def find_or_create_location(
        self,
        address: str,
        latitude: float,
        longitude: float,
        formatted_address: Optional[str] = None,
    ) -> Location:
        # Look for an existing location within a small radius (e.g., 100 meters)
        RADIUS = 0.001  # Approximately 100 meters
        result = await self.db.execute(
            select(Location).where(
                Location.latitude.between(latitude - RADIUS, latitude + RADIUS),
                Location.longitude.between(longitude - RADIUS, longitude + RADIUS),
            )
        )
        existing_location = result.scalars().first()

        if existing_location:
            # Update last_verified timestamp if it's older than a week
            if datetime.utcnow() - existing_location.last_verified > timedelta(days=7):
                existing_location.last_verified = datetime.utcnow()
                await self.db.commit()
            return existing_location

        # Create new location if none exists
        new_location = Location(
            address=address,
            latitude=latitude,
            longitude=longitude,
            formatted_address=formatted_address or address,
            last_verified=datetime.utcnow(),
        )
        self.db.add(new_location)
        await self.db.commit()
        await self.db.refresh(new_location)
        return new_location

    async def get_nearby_locations(
        self, latitude: float, longitude: float, radius_km: float = 1.0
    ) -> list[Location]:
        # Convert km to degrees (approximate)
        radius_degrees = radius_km / 111.0  # 1 degree ≈ 111 km

        result = await self.db.execute(
            select(Location).where(
                Location.latitude.between(
                    latitude - radius_degrees, latitude + radius_degrees
                ),
                Location.longitude.between(
                    longitude - radius_degrees, longitude + radius_degrees
                ),
            )
        )
        return result.scalars().all()
