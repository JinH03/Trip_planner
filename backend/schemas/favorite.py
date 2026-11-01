
from pydantic import BaseModel, Field

from backend.schemas.place import PlaceResponse


class FavoriteCreate(BaseModel):
    place_id: int = Field(gt=0)


class FavoriteResponse(BaseModel):
    id: int
    place_id: int
    place: PlaceResponse

    model_config = {"from_attributes": True}
