from pydantic import BaseModel, Field
from typing import List
from datetime import datetime

class RecurringPatternBase(BaseModel):
    days_of_week: List[int] = Field(..., description="List of days (1-7, where 1 is Monday)")
    start_date: datetime
    end_date: datetime

class RecurringPatternCreate(RecurringPatternBase):
    pass

class RecurringPattern(RecurringPatternBase):
    id: int
    ride_id: int

    class Config:
        from_attributes = True 
