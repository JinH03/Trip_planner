from datetime import date, datetime

from pydantic import BaseModel


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
