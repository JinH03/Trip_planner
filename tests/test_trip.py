from unittest.mock import patch

from backend.services import place as place_service


def test_get_trips_without_token(client):
    response = client.get("/trips")

    assert response.status_code == 401


def test_create_trip(client, auth_headers):
    response = client.post(
        "/trips",
        headers=auth_headers,
        json={
            "title": "오사카 여행",
            "destination": "오사카",
            "start_date": "2026-10-10",
            "end_date": "2026-10-12",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["title"] == "오사카 여행"
    assert data["destination"] == "오사카"
    assert data["start_date"] == "2026-10-10"
    assert data["end_date"] == "2026-10-12"


def test_create_trip_creates_trip_days(
    client,
    auth_headers,
):
    create_response = client.post(
        "/trips",
        headers=auth_headers,
        json={
            "title": "도쿄 여행",
            "destination": "도쿄",
            "start_date": "2026-10-10",
            "end_date": "2026-10-12",
        },
    )

    assert create_response.status_code == 201

    trip_id = create_response.json()["id"]
    detail_response = client.get(
        f"/trips/{trip_id}/detail",
        headers=auth_headers,
    )

    assert detail_response.status_code == 200

    data = detail_response.json()
    assert len(data["days"]) == 3

    assert data["days"][0]["day_number"] == 1
    assert data["days"][0]["date"] == "2026-10-10"

    assert data["days"][1]["day_number"] == 2
    assert data["days"][1]["date"] == "2026-10-11"

    assert data["days"][2]["day_number"] == 3
    assert data["days"][2]["date"] == "2026-10-12"


def test_update_trip_expands_trip_days(
    client,
    auth_headers,
):
    create_response = client.post(
        "/trips",
        headers=auth_headers,
        json={
            "title": "부산 여행",
            "destination": "부산",
            "start_date": "2026-10-10",
            "end_date": "2026-10-11",
        },
    )

    assert create_response.status_code == 201

    trip_id = create_response.json()["id"]
    update_response = client.put(
        f"/trips/{trip_id}",
        headers=auth_headers,
        json={
            "title": "부산 여행 수정",
            "destination": "부산",
            "start_date": "2026-10-10",
            "end_date": "2026-10-13",
        },
    )

    assert update_response.status_code == 200
    detail_response = client.get(
        f"/trips/{trip_id}/detail",
        headers=auth_headers,
    )

    assert detail_response.status_code == 200

    data = detail_response.json()
    assert len(data["days"]) == 4

    assert data["days"][0]["day_number"] == 1
    assert data["days"][0]["date"] == "2026-10-10"

    assert data["days"][1]["day_number"] == 2
    assert data["days"][1]["date"] == "2026-10-11"

    assert data["days"][2]["day_number"] == 3
    assert data["days"][2]["date"] == "2026-10-12"

    assert data["days"][3]["day_number"] == 4
    assert data["days"][3]["date"] == "2026-10-13"


def test_update_trip_shrinks_trip_days(
    client,
    auth_headers,
):
    create_response = client.post(
        "/trips",
        headers=auth_headers,
        json={
            "title": "제주 여행",
            "destination": "제주",
            "start_date": "2026-10-10",
            "end_date": "2026-10-13",
        },
    )

    assert create_response.status_code == 201

    trip_id = create_response.json()["id"]
    update_response = client.put(
        f"/trips/{trip_id}",
        headers=auth_headers,
        json={
            "title": "제주 여행",
            "destination": "제주",
            "start_date": "2026-10-10",
            "end_date": "2026-10-11",
        },
    )

    assert update_response.status_code == 200
    detail_response = client.get(
        f"/trips/{trip_id}/detail",
        headers=auth_headers,
    )

    assert detail_response.status_code == 200

    data = detail_response.json()
    assert len(data["days"]) == 2

    assert data["days"][0]["day_number"] == 1
    assert data["days"][0]["date"] == "2026-10-10"

    assert data["days"][1]["day_number"] == 2
    assert data["days"][1]["date"] == "2026-10-11"


def test_create_trip_with_blank_title(
    client,
    auth_headers,
):
    response = client.post(
        "/trips",
        headers=auth_headers,
        json={
            "title": "     ",
            "destination": "오사카",
            "start_date": "2026-10-10",
            "end_date": "2026-10-12",
        },
    )

    assert response.status_code == 422


def test_create_trip_with_blank_destination(
    client,
    auth_headers,
):
    response = client.post(
        "/trips",
        headers=auth_headers,
        json={
            "title": "오사카 여행",
            "destination": "     ",
            "start_date": "2026-10-10",
            "end_date": "2026-10-12",
        },
    )

    assert response.status_code == 422


def test_create_trip_with_too_long_title(
    client,
    auth_headers,
):
    response = client.post(
        "/trips",
        headers=auth_headers,
        json={
            "title": "가" * 201,
            "destination": "오사카",
            "start_date": "2026-10-10",
            "end_date": "2026-10-12",
        },
    )

    assert response.status_code == 422


def test_create_trip_with_invalid_date_range(
    client,
    auth_headers,
):
    response = client.post(
        "/trips",
        headers=auth_headers,
        json={
            "title": "오사카 여행",
            "destination": "오사카",
            "start_date": "2026-10-12",
            "end_date": "2026-10-10",
        },
    )

    assert response.status_code == 400


@patch("backend.services.place.httpx.post")
def test_search_places_with_trip_id_uses_destination_bias(
    mock_post,
    client,
    auth_headers,
):
    trip_response = client.post(
        "/trips",
        headers=auth_headers,
        json={
            "title": "오사카 여행",
            "destination": "오사카",
            "start_date": "2026-10-20",
            "end_date": "2026-10-21",
        },
    )

    assert trip_response.status_code == 201

    trip_id = trip_response.json()["id"]

    mock_post.side_effect = [
        # 1번째 호출:
        # destination = "오사카" 좌표 조회
        type(
            "MockResponse",
            (),
            {
                "status_code": 200,
                "raise_for_status": lambda self: None,
                "json": lambda self: {
                    "places": [
                        {
                            "location": {
                                "latitude": 34.6937,
                                "longitude": 135.5023,
                            }
                        }
                    ]
                },
            },
        )(),

        # 2번째 호출:
        # 실제 스타벅스 검색
        type(
            "MockResponse",
            (),
            {
                "status_code": 200,
                "raise_for_status": lambda self: None,
                "json": lambda self: {
                    "places": [
                        {
                            "id": "test-starbucks-osaka",
                            "formattedAddress": "Osaka, Japan",
                            "location": {
                                "latitude": 34.7000,
                                "longitude": 135.5000,
                            },
                            "displayName": {
                                "text": "스타벅스 오사카",
                                "languageCode": "ko",
                            },
                            "primaryType": "coffee_shop",
                        }
                    ]
                },
            },
        )(),
    ]

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
                "trip_id": trip_id,
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "스타벅스 오사카"

    assert mock_post.call_count == 2

    first_call = mock_post.call_args_list[0]
    first_body = first_call.kwargs["json"]

    assert first_body["textQuery"] == "오사카"
    assert first_body["pageSize"] == 1

    second_call = mock_post.call_args_list[1]
    second_body = second_call.kwargs["json"]

    assert second_body["textQuery"] == "스타벅스"

    assert (
        second_body["locationBias"]["circle"]["center"]["latitude"]
        == 34.6937
    )

    assert (
        second_body["locationBias"]["circle"]["center"]["longitude"]
        == 135.5023
    )