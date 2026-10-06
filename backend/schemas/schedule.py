from datetime import datetime, time

from pydantic import BaseModel, Field


class ScheduleCreate(BaseModel):
    title: str
    start_time: time | None = None
    place: str | None = None
    memo: str | None = None
    order_index: int = 0


class ScheduleUpdate(BaseModel):
    title: str
    start_time: time | None = None
    place: str | None = None
    memo: str | None = None
    order_index: int = 0


class ScheduleResponse(BaseModel):
    id: int
    trip_day_id: int
    title: str
    start_time: time | None
    place: str | None
    memo: str | None
    order_index: int
    created_at: datetime

    model_config = {
        "from_attributes": True
    }
class ScheduleOrderItem(BaseModel):
    schedule_id: int
    order_index: int = Field(ge= 0)


class ScheduleReorderRequest(BaseModel):
    schedules: list[ScheduleOrderItem]