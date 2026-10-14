from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.schemas.place import (
    PlaceCreate,
    PlaceResponse,
    PlaceSearchResult,
)
from backend.services.place import (
    create_place_service,
    search_places_service,
)


router = APIRouter(
    prefix="/places",
    tags=["places"],
)


@router.get(
    "/search",
    response_model=list[PlaceSearchResult],
)
def search_places(
    query: str = Query(
        min_length=1,
        max_length=100,
    ),
    latitude: float | None = Query(
        default= None,
        ge = -90,
        le=90,
    ),
    longitude: float | None = Query(
        default=None,
        ge=-180,
        le=180,
    ),
):
    return search_places_service(
        query=query,
        latitude=latitude,
        longitude=longitude,
    )


@router.post(
    "",
    response_model=PlaceResponse,
    status_code=201,
)
def create_place(
    place: PlaceCreate,
    db: Session = Depends(get_db),
):
    return create_place_service(
        db=db,
        place_data=place,
    )