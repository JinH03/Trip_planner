from datetime import datetime, time

from pydantic import BaseModel, Field, field_validator

from backend.schemas.place import PlaceResponse


class ScheduleCreate(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=200,
    )

    start_time: time | None = None

    place: str | None = Field(
        default=None,
        max_length=200,
    )

    place_id: int | None = Field(
        default=None,
        gt=0,
    )

    memo: str | None = Field(
        default=None,
        max_length=500,
    )

    order_index: int = Field(
        default=0,
        ge=0,
    )

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str):
        value = value.strip()

        if not value:
            raise ValueError(
                "Title cannot be empty"
            )

        return value


class ScheduleUpdate(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=200,
    )

    start_time: time | None = None

    place: str | None = Field(
        default=None,
        max_length=200,
    )

    place_id: int | None = Field(
        default=None,
        gt=0,
    )

    memo: str | None = Field(
        default=None,
        max_length=500,
    )

    order_index: int = Field(
        default=0,
        ge=0,
    )

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str):
        value = value.strip()

        if not value:
            raise ValueError(
                "Title cannot be empty"
            )

        return value


class ScheduleResponse(BaseModel):
    id: int
    trip_day_id: int
    title: str
    start_time: time | None
    place: str | None
    place_id: int | None
    place_info: PlaceResponse | None
    memo: str | None
    order_index: int
    created_at: datetime

    model_config = {
        "from_attributes": True
    }


class ScheduleOrderItem(BaseModel):
    schedule_id: int = Field(
        gt=0,
    )

    order_index: int = Field(
        ge=0,
    )


class ScheduleReorderRequest(BaseModel):
    schedules: list[ScheduleOrderItem] = Field(
        min_length=1,
    )