from pydantic import BaseModel, Field
from typing import Optional

class LocationBase(BaseModel):
    address: str
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    formatted_address: Optional[str] = None

class LocationCreate(LocationBase):
    pass

class Location(LocationBase):
    id: int
    last_verified: Optional[str] = None

    class Config:
        from_attributes = True 
