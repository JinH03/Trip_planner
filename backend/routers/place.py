from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.dependencies.auth import get_current_user
from backend.dependencies.ownership import get_owned_trip
from backend.models import User
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
@router.get("/search", response_model=list[PlaceSearchResult])
def search_places(
    query: str = Query(min_length=1, max_length=100),
    trip_id: int | None = Query(default=None, gt=0),
    latitude: float | None = Query(default=None, ge=-90, le=90),
    longitude: float | None = Query(default=None, ge=-180, le=180),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if trip_id is not None:
        trip = get_owned_trip(
            db=db,
            trip_id=trip_id,
            user_id=current_user.id,
        )

        if latitude is None and longitude is None:
            latitude = trip.destination_latitude
            longitude = trip.destination_longitude

    return search_places_service(
        query=query,
        latitude=latitude,
        longitude=longitude,
    )