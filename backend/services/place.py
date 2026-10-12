from sqlalchemy.orm import Session

from backend.models import Place
from backend.schemas.place import PlaceCreate, PlaceSearchResult


def search_places_service(
    query: str,
) -> list[PlaceSearchResult]:
    query = query.strip()

    if not query:
        return []

    dummy_places = [
        PlaceSearchResult(
            name="오사카성",
            address="1-1 Osakajo, Chuo Ward, Osaka",
            latitude=34.6873,
            longitude=135.5262,
            category="관광지",
            external_place_id="dummy-osaka-castle",
        ),
        PlaceSearchResult(
            name="도톤보리",
            address="Dotonbori, Chuo Ward, Osaka",
            latitude=34.6687,
            longitude=135.5013,
            category="관광지",
            external_place_id="dummy-dotonbori",
        ),
    ]

    return [
        place
        for place in dummy_places
        if query.lower() in place.name.lower()
    ]


def create_place_service(
    db: Session,
    place_data: PlaceCreate,
) -> Place:
    if place_data.external_place_id:
        existing_place = (
            db.query(Place)
            .filter(
                Place.external_place_id
                == place_data.external_place_id
            )
            .first()
        )

        if existing_place:
            return existing_place

    new_place = Place(
        name=place_data.name,
        address=place_data.address,
        latitude=place_data.latitude,
        longitude=place_data.longitude,
        category=place_data.category,
        external_place_id=place_data.external_place_id,
    )

    try:
        db.add(new_place)
        db.commit()
        db.refresh(new_place)

        return new_place

    except Exception:
        db.rollback()
        raise