from unittest.mock import patch

from backend.services import place as place_service


def test_create_place(client):
    response = client.post(
        "/places",
        json={
            "name": "오사카성",
            "address": "1-1 Osakajo, Chuo Ward, Osaka",
            "latitude": 34.6873,
            "longitude": 135.5262,
            "category": "castle",
            "external_place_id": "test-osaka-castle",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["id"] is not None
    assert data["name"] == "오사카성"
    assert data["external_place_id"] == "test-osaka-castle"


def test_create_duplicate_place_returns_existing_place(client):
    place_data = {
        "name": "오사카성",
        "address": "1-1 Osakajo, Chuo Ward, Osaka",
        "latitude": 34.6873,
        "longitude": 135.5262,
        "category": "castle",
        "external_place_id": "test-osaka-castle",
    }

    first_response = client.post(
        "/places",
        json=place_data,
    )

    second_response = client.post(
        "/places",
        json=place_data,
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 201

    first_data = first_response.json()
    second_data = second_response.json()

    assert first_data["id"] == second_data["id"]


@patch("backend.services.place.httpx.post")
def test_search_places(mock_post, client):
    mock_post.return_value.status_code = 200

    mock_post.return_value.json.return_value = {
        "places": [
            {
                "id": "ChIJ_test_osaka_castle",
                "formattedAddress": (
                    "1-1 Osakajo, Chuo Ward, Osaka, Japan"
                ),
                "location": {
                    "latitude": 34.6872571,
                    "longitude": 135.5258546,
                },
                "displayName": {
                    "text": "Osaka Castle",
                    "languageCode": "en",
                },
                "primaryType": "castle",
            }
        ]
    }

    mock_post.return_value.raise_for_status.return_value = None

    with patch.object(
        place_service,
        "GOOGLE_PLACES_API_KEY",
        "test-api-key",
    ):
        response = client.get(
            "/places/search",
            params={
                "query": "오사카성",
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1

    assert data[0]["name"] == "Osaka Castle"
    assert data[0]["category"] == "castle"
    assert data[0]["external_place_id"] == (
        "ChIJ_test_osaka_castle"
    )

    assert data[0]["latitude"] == 34.6872571
    assert data[0]["longitude"] == 135.5258546


@patch("backend.services.place.httpx.post")
def test_search_places_empty_result(mock_post, client):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {
        "places": []
    }

    mock_post.return_value.raise_for_status.return_value = None

    with patch.object(
        place_service,
        "GOOGLE_PLACES_API_KEY",
        "test-api-key",
    ):
        response = client.get(
            "/places/search",
            params={
                "query": "없는장소",
            },
        )

    assert response.status_code == 200
    assert response.json() == []