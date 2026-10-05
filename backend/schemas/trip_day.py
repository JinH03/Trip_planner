from datetime import date, datetime

from pydantic import BaseModel
from backend.schemas.schedule import ScheduleResponse

class TripDayCreate(BaseModel):
    day_number: int
    date: date


class TripDayResponse(BaseModel):
    id: int
    trip_id: int
    day_number: int
    date: date
    created_at: datetime

    model_config = {
        "from_attributes": True
    }

class TripDayUpdate(BaseModel):
    day_number: int
    date: date

class TripDayWithSchedules(BaseModel):
    id: int
    trip_id: int
    day_number: int
    date: date
    created_at: datetime
    schedules: list[ScheduleResponse]

    model_config = {"from_attributes": True}