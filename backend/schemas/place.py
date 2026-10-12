from datetime import datetime

from pydantic import BaseModel, Field


class PlaceCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=200,
    )

    address: str | None = Field(
        default=None,
        max_length=300,
    )

    latitude: float | None = None
    longitude: float | None = None

    category: str | None = Field(
        default=None,
        max_length=100,
    )

    external_place_id: str | None = Field(
        default=None,
        max_length=255,
    )


class PlaceResponse(BaseModel):
    id: int
    name: str
    address: str | None
    latitude: float | None
    longitude: float | None
    category: str | None
    external_place_id: str | None
    created_at: datetime

    model_config = {
        "from_attributes": True
    }


class PlaceSearchResult(BaseModel):
    name: str
    address: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    category: str | None = None
    external_place_id: str | None = None

