
from unittest.mock import patch

import httpx
import pytest
from fastapi import HTTPException

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
def test_search_places(
    mock_post,
    client,
    auth_headers,
):
    mock_post.return_value.status_code = 200
    mock_post.return_value.raise_for_status.return_value = None

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

    with patch.object(
        place_service,
        "GOOGLE_PLACES_API_KEY",
        "test-api-key",
    ):
        response = client.get(
            "/places/search",
            headers=auth_headers,
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
def test_search_places_empty_result(
    mock_post,
    client,
    auth_headers,
):
    mock_post.return_value.status_code = 200
    mock_post.return_value.raise_for_status.return_value = None

    mock_post.return_value.json.return_value = {
        "places": []
    }

    with patch.object(
        place_service,
        "GOOGLE_PLACES_API_KEY",
        "test-api-key",
    ):
        response = client.get(
            "/places/search",
            headers=auth_headers,
            params={
                "query": "없는장소",
            },
        )

    assert response.status_code == 200
    assert response.json() == []


@patch("backend.services.place.httpx.post")
def test_search_places_with_location_bias(
    mock_post,
    client,
    auth_headers,
):
    mock_post.return_value.status_code = 200
    mock_post.return_value.raise_for_status.return_value = None

    mock_post.return_value.json.return_value = {
        "places": []
    }

    with patch.object(
        place_service,
        "GOOGLE_PLACES_API_KEY",
        "test-api-key",
    ):
        response = client.get(
            "/places/search",
            headers=auth_headers,
            params={
                "query": "스타벅스",
                "latitude": 34.6937,
                "longitude": 135.5023,
            },
        )

    assert response.status_code == 200

    _, kwargs = mock_post.call_args
    body = kwargs["json"]

    assert body["textQuery"] == "스타벅스"
    assert body["languageCode"] == "ko"
    assert body["pageSize"] == 5

    assert (
        body["locationBias"]["circle"]["center"]["latitude"]
        == 34.6937
    )

    assert (
        body["locationBias"]["circle"]["center"]["longitude"]
        == 135.5023
    )

    assert body["locationBias"]["circle"]["radius"] == 10000.0


@patch("backend.services.place.httpx.post")
def test_search_places_without_location_bias(
    mock_post,
    client,
    auth_headers,
):
    mock_post.return_value.status_code = 200
    mock_post.return_value.raise_for_status.return_value = None

    mock_post.return_value.json.return_value = {
        "places": []
    }

    with patch.object(
        place_service,
        "GOOGLE_PLACES_API_KEY",
        "test-api-key",
    ):
        response = client.get(
            "/places/search",
            headers=auth_headers,
            params={
                "query": "스타벅스",
            },
        )

    assert response.status_code == 200

    _, kwargs = mock_post.call_args
    body = kwargs["json"]

    assert "locationBias" not in body


def test_create_place_with_blank_name(client):
    response = client.post(
        "/places",
        json={
            "name": "   ",
            "address": "test address",
            "latitude": 34.6873,
            "longitude": 135.5262,
            "category": "castle",
            "external_place_id": "blank-name-test",
        },
    )

    assert response.status_code == 422


def test_create_place_with_invalid_latitude(client):
    response = client.post(
        "/places",
        json={
            "name": "오사카성",
            "address": "test address",
            "latitude": 91,
            "longitude": 135.5262,
            "category": "castle",
            "external_place_id": "invalid-latitude-test",
        },
    )

    assert response.status_code == 422


def test_create_place_with_invalid_longitude(client):
    response = client.post(
        "/places",
        json={
            "name": "오사카성",
            "address": "test address",
            "latitude": 34.6873,
            "longitude": 181,
            "category": "castle",
            "external_place_id": "invalid-longitude-test",
        },
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    "google_status, expected_status, expected_calls",
    [
        (400, 502, 1),
        (403, 502, 1),
        (429, 503, 3),
        (500, 503, 3),
        (503, 503, 3),
    ],
)
@patch("backend.services.place.time.sleep")
@patch("backend.services.place.httpx.post")
def test_google_places_http_errors(
    mock_post,
    mock_sleep,
    google_status,
    expected_status,
    expected_calls,
):
    request = httpx.Request(
        "POST",
        place_service.GOOGLE_PLACES_SEARCH_URL,
    )

    response = httpx.Response(
        status_code=google_status,
        request=request,
    )

    mock_post.return_value = response

    with patch.object(
        place_service,
        "GOOGLE_PLACES_API_KEY",
        "test-api-key",
    ):
        with pytest.raises(HTTPException) as exc_info:
            place_service.search_places_service(
                query="스타벅스",
            )

    assert exc_info.value.status_code == expected_status
    assert mock_post.call_count == expected_calls

    if expected_calls == 3:
        assert mock_sleep.call_count == 2
    else:
        mock_sleep.assert_not_called()


@patch("backend.services.place.time.sleep")
@patch("backend.services.place.httpx.post")
def test_google_places_timeout(
    mock_post,
    mock_sleep,
):
    mock_post.side_effect = httpx.ReadTimeout(
        "Google Places API timed out"
    )

    with patch.object(
        place_service,
        "GOOGLE_PLACES_API_KEY",
        "test-api-key",
    ):
        with pytest.raises(HTTPException) as exc_info:
            place_service.search_places_service(
                query="스타벅스",
            )

    assert exc_info.value.status_code == 504
    assert mock_post.call_count == 3
    assert mock_sleep.call_count == 2


@patch("backend.services.place.httpx.post")
def test_google_places_connection_error(mock_post):
    mock_post.side_effect = httpx.ConnectError(
        "Connection failed"
    )

    with patch.object(
        place_service,
        "GOOGLE_PLACES_API_KEY",
        "test-api-key",
    ):
        with pytest.raises(HTTPException) as exc_info:
            place_service.search_places_service(
                query="스타벅스",
            )

    assert exc_info.value.status_code == 502
    assert mock_post.call_count == 1


@patch("backend.services.place.time.sleep")
@patch("backend.services.place.httpx.post")
def test_google_places_retry_then_success(
    mock_post,
    mock_sleep,
):
    request = httpx.Request(
        "POST",
        place_service.GOOGLE_PLACES_SEARCH_URL,
    )

    mock_post.side_effect = [
        # 첫 번째 요청: Google API 503
        httpx.Response(
            status_code=503,
            request=request,
        ),

        # 두 번째 요청: 정상 응답
        httpx.Response(
            status_code=200,
            request=request,
            json={
                "places": []
            },
        ),
    ]

    with patch.object(
        place_service,
        "GOOGLE_PLACES_API_KEY",
        "test-api-key",
    ):
        result = place_service.search_places_service(
            query="스타벅스",
        )

    assert result == []
    assert mock_post.call_count == 2
    mock_sleep.assert_called_once_with(0.2)
