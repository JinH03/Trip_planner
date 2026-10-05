from datetime import date, datetime

from pydantic import BaseModel
from backend.schemas.trip_day import TripDayWithSchedules

class TripCreate(BaseModel):
    title: str
    destination: str
    start_date: date
    end_date: date


class TripResponse(BaseModel):
    id: int
    title: str
    destination: str
    start_date: date
    end_date: date
    created_at: datetime

    model_config = {
        "from_attributes": True
    }

class TripUpdate(BaseModel):
    title: str 
    destination: str 
    start_date: date 
    end_date: date 

class TripDetailResponse(BaseModel):
    id: int
    title: str
    destination: str
    start_date: date
    end_date: date
    created_at: datetime
    days: list[TripDayWithSchedules]

    model_config = {"from_attributes": True}