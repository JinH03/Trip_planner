
import os

import httpx
from dotenv import load_dotenv
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
import time
from backend.models import Place
from backend.schemas.place import (
    PlaceCreate,
    PlaceSearchResult,
)


load_dotenv()

GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")

GOOGLE_PLACES_SEARCH_URL = (
    "https://places.googleapis.com/v1/places:searchText"
)


def request_google_places(
    body: dict,
    field_mask: str,
) -> dict:
    if not GOOGLE_PLACES_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="Google Places API key is not configured",
        )

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_PLACES_API_KEY,
        "X-Goog-FieldMask": field_mask,
    }

    max_attempts = 3

    for attempt in range(max_attempts):
        try:
            response = httpx.post(
                GOOGLE_PLACES_SEARCH_URL,
                headers=headers,
                json=body,
                timeout=10.0,
            )

            response.raise_for_status()
            return response.json()

        except httpx.TimeoutException as exc:
            if attempt == max_attempts - 1:
                raise HTTPException(
                    status_code=504,
                    detail="Google Places API timeout",
                ) from exc

        except httpx.HTTPStatusError as exc:
            google_status = exc.response.status_code

            if google_status == 429 or google_status >= 500:
                if attempt == max_attempts - 1:
                    raise HTTPException(
                        status_code=503,
                        detail="Google Places API temporarily unavailable",
                    ) from exc
            else:
                raise HTTPException(
                    status_code=502,
                    detail="Google Places API request failed",
                ) from exc

        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=502,
                detail="Google Places API connection failed",
            ) from exc

        time.sleep(0.2 * (2 ** attempt))

    raise RuntimeError("Unexpected retry state")

def resolve_destination_coordinates(
    destination: str,
) -> tuple[float | None, float | None]:
    """
    여행 목적지를 위도/경도로 변환한다.
    """

    body = {
        "textQuery": destination,
        "languageCode": "ko",
        "pageSize": 1,
    }

    data = request_google_places(
        body=body,
        field_mask="places.location",
    )

    places = data.get("places", [])

    if not places:
        return None, None

    location = places[0].get("location", {})

    return (
        location.get("latitude"),
        location.get("longitude"),
    )


def search_places_service(
    query: str,
    latitude: float | None = None,
    longitude: float | None = None,
) -> list[PlaceSearchResult]:
    """
    Google Places에서 장소를 검색한다.

    좌표가 있으면 locationBias를 적용한다.
    """

    query = query.strip()

    if not query:
        return []

    body = {
        "textQuery": query,
        "languageCode": "ko",
        "pageSize": 5,
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

    field_mask = (
        "places.id,"
        "places.displayName,"
        "places.formattedAddress,"
        "places.location,"
        "places.primaryType"
    )

    data = request_google_places(
        body=body,
        field_mask=field_mask,
    )

    places = data.get("places", [])[:5]

    results = []

    for place in places:
        display_name = place.get("displayName", {})
        location = place.get("location", {})

        results.append(
            PlaceSearchResult(
                name=display_name.get("text", ""),
                address=place.get("formattedAddress"),
                latitude=location.get("latitude"),
                longitude=location.get("longitude"),
                category=place.get("primaryType"),
                external_place_id=place.get("id"),
            )
        )

    return results


def create_place_service(
    db: Session,
    place_data: PlaceCreate,
) -> Place:
    """
    Place를 DB에 저장한다.
    같은 external_place_id가 있으면 기존 Place를 반환한다.
    """

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
