from typing import Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.location import Location
from app.schemas.location import LocationCreate
from app.core.maps import reverse_geocode

class LocationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def find_or_create_location(
        self,
        address: str,
        latitude: float,
        longitude: float,
        formatted_address: Optional[str] = None
    ) -> Location:
        """
        Find an existing location or create a new one
        """
        # Try to find existing location
        result = await self.db.execute(
            select(Location).filter(
                Location.latitude == latitude,
                Location.longitude == longitude
            )
        )
        location = result.scalars().first()

        if not location:
            # Create new location if not found
            if not formatted_address:
                formatted_address = await reverse_geocode((latitude, longitude))
            
            location = Location(
                address=address,
                latitude=latitude,
                longitude=longitude,
                formatted_address=formatted_address
            )
            self.db.add(location)
            await self.db.flush()
            await self.db.refresh(location)

        return location

    async def get_location_by_id(self, location_id: int) -> Optional[Location]:
        """
        Get a location by ID
        """
        result = await self.db.execute(
            select(Location).filter(Location.id == location_id)
        )
        return result.scalars().first()

    async def update_location(
        self,
        location_id: int,
        location_update: LocationCreate
    ) -> Optional[Location]:
        """
        Update a location's details
        """
        location = await self.get_location_by_id(location_id)
        if not location:
            return None

        for field, value in location_update.dict(exclude_unset=True).items():
            setattr(location, field, value)

        await self.db.commit()
        await self.db.refresh(location)
        return location 
