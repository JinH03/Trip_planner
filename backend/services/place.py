import os

import httpx
from dotenv import load_dotenv
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.models import Place
from backend.schemas.place import (
    PlaceCreate,
    PlaceSearchResult,
)


load_dotenv()


GOOGLE_PLACES_API_KEY = os.getenv(
    "GOOGLE_PLACES_API_KEY"
)

GOOGLE_PLACES_SEARCH_URL = (
    "https://places.googleapis.com/v1/places:searchText"
)


def search_places_service(
    query: str,
    latitude: float | None = None,
    longitude: float | None = None,
) -> list[PlaceSearchResult]:

    query = query.strip()

    if not query:
        return []

    if not GOOGLE_PLACES_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google Places API key is not configured",
        )

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_PLACES_API_KEY,
        "X-Goog-FieldMask": (
            "places.id,"
            "places.displayName,"
            "places.formattedAddress,"
            "places.location,"
            "places.primaryType"
        ),
    }

    body = {
        "textQuery": query,
        "languageCode": "ko",
        "pageSize": 5
    }
    if latitude is not None and longitude is not None:
        body["locationBias"] = {
            "circle": {
                "center": {
                    "latitude": latitude,
                    "longitude": longitude,
                },
                "radius": 10000.0,
            }
        }
    try:
        response = httpx.post(
            GOOGLE_PLACES_SEARCH_URL,
            headers=headers,
            json=body,
            timeout=10.0,
        )

        response.raise_for_status()

    except httpx.HTTPStatusError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Google Places API request failed",
        )

    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Google Places API connection failed",
        )

    data = response.json()

    places = data.get(
        "places",
        [],
    )[:5]

    results = []

    for place in places:
        display_name = place.get(
            "displayName",
            {},
        )

        location = place.get(
            "location",
            {},
        )

        results.append(
            PlaceSearchResult(
                name=display_name.get(
                    "text",
                    "",
                ),
                address=place.get(
                    "formattedAddress"
                ),
                latitude=location.get(
                    "latitude"
                ),
                longitude=location.get(
                    "longitude"
                ),
                category=place.get(
                    "primaryType"
                ),
                external_place_id=place.get(
                    "id"
                ),
            )
        )

    return results


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