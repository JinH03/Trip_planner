from datetime import date, datetime

from pydantic import BaseModel, Field, field_validator

from backend.schemas.trip_day import TripDayWithSchedules


class TripCreate(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=200,
    )

    destination: str = Field(
        min_length=1,
        max_length=200,
    )

    start_date: date
    end_date: date

    @field_validator(
        "title",
        "destination",
    )
    @classmethod
    def validate_text(cls, value: str):
        value = value.strip()

        if not value:
            raise ValueError(
                "Value cannot be empty"
            )

        return value


class TripUpdate(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=200,
    )

    destination: str = Field(
        min_length=1,
        max_length=200,
    )

    start_date: date
    end_date: date

    @field_validator(
        "title",
        "destination",
    )
    @classmethod
    def validate_text(cls, value: str):
        value = value.strip()

        if not value:
            raise ValueError(
                "Value cannot be empty"
            )

        return value


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


class TripDetailResponse(BaseModel):
    id: int
    title: str
    destination: str
    start_date: date
    end_date: date
    created_at: datetime
    days: list[TripDayWithSchedules]

    model_config = {
        "from_attributes": True
    }