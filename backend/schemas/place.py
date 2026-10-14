from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class PlaceCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=200,
    )

    address: str | None = Field(
        default=None,
        max_length=300,
    )

    latitude: float | None = Field(
        default=None,
        ge=-90,
        le=90,
    )

    longitude: float | None = Field(
        default=None,
        ge=-180,
        le=180,
    )
    category: str | None = Field(
        default=None,
        max_length=100,
    )

    external_place_id: str | None = Field(
        default=None,
        max_length=255,
    )
    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str):
        value = value.strip()

        if not value:
            raise ValueError(
                "Place name cannot be empty"
            )

        return value

class PlaceResponse(BaseModel):
    id: int
    name: str
    address: str | None
    latitude: float | None = Field(
        default=None,
        ge=-90,
        le=90,
    )

    longitude: float | None = Field(
        default=None,
        ge=-180,
        le=180,
    )
    category: str | None
    external_place_id: str | None
    created_at: datetime

    model_config = {
        "from_attributes": True
    }


class PlaceSearchResult(BaseModel):
    name: str
    address: str | None = None
    latitude: float | None = Field(
        default=None,
        ge=-90,
        le=90,
    )

    longitude: float | None = Field(
        default=None,
        ge=-180,
        le=180,
    )
    category: str | None = None
    external_place_id: str | None = None

