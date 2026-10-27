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
def test_search_places_with_trip_id_uses_saved_coordinates(
    mock_post,
    client,
    auth_headers,
):
    # Trip 생성 시 destination 좌표 조회용 응답
    mock_post.side_effect = [
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
        # 실제 장소 검색 응답
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

    # 1번째 호출 = Trip 생성 시 목적지 좌표 조회
    first_call = mock_post.call_args_list[0]
    first_body = first_call.kwargs["json"]

    assert first_body["textQuery"] == "오사카"
    assert first_body["pageSize"] == 1

    # 2번째 호출 = 장소 검색
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

@patch("backend.services.place.httpx.post")
def test_create_trip_saves_destination_coordinates(
    mock_post,
    client,
    auth_headers,
):
    mock_post.return_value.status_code = 200
    mock_post.return_value.raise_for_status.return_value = None
    mock_post.return_value.json.return_value = {
        "places": [
            {
                "location": {
                    "latitude": 34.6937,
                    "longitude": 135.5023,
                }
            }
        ]
    }

    with patch.object(
        place_service,
        "GOOGLE_PLACES_API_KEY",
        "test-api-key",
    ):
        response = client.post(
            "/trips",
            headers=auth_headers,
            json={
                "title": "오사카 여행",
                "destination": "오사카",
                "start_date": "2026-10-20",
                "end_date": "2026-10-21",
            },
        )

    assert response.status_code == 201

    data = response.json()

    assert data["destination"] == "오사카"
    assert data["destination_latitude"] == 34.6937
    assert data["destination_longitude"] == 135.5023

    assert mock_post.call_count == 1

    _, kwargs = mock_post.call_args
    body = kwargs["json"]

    assert body["textQuery"] == "오사카"
    assert body["pageSize"] == 1

@patch("backend.services.place.httpx.post")
def test_update_trip_refreshes_destination_coordinates(
    mock_post,
    client,
    auth_headers,
):
    mock_post.side_effect = [
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
                                "latitude": 35.6762,
                                "longitude": 139.6503,
                            }
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
        create_response = client.post(
            "/trips",
            headers=auth_headers,
            json={
                "title": "일본 여행",
                "destination": "오사카",
                "start_date": "2026-10-20",
                "end_date": "2026-10-21",
            },
        )

        assert create_response.status_code == 201

        trip_id = create_response.json()["id"]

        update_response = client.put(
            f"/trips/{trip_id}",
            headers=auth_headers,
            json={
                "title": "일본 여행",
                "destination": "도쿄",
                "start_date": "2026-10-20",
                "end_date": "2026-10-21",
            },
        )

    assert update_response.status_code == 200

    data = update_response.json()

    assert data["destination"] == "도쿄"
    assert data["destination_latitude"] == 35.6762
    assert data["destination_longitude"] == 139.6503

    assert mock_post.call_count == 2


@patch("backend.services.place.httpx.post")
def test_update_trip_does_not_refresh_coordinates_when_destination_unchanged(
    mock_post,
    client,
    auth_headers,
):
    mock_post.return_value.status_code = 200
    mock_post.return_value.raise_for_status.return_value = None
    mock_post.return_value.json.return_value = {
        "places": [
            {
                "location": {
                    "latitude": 34.6937,
                    "longitude": 135.5023,
                }
            }
        ]
    }

    with patch.object(
        place_service,
        "GOOGLE_PLACES_API_KEY",
        "test-api-key",
    ):
        create_response = client.post(
            "/trips",
            headers=auth_headers,
            json={
                "title": "오사카 여행",
                "destination": "오사카",
                "start_date": "2026-10-20",
                "end_date": "2026-10-21",
            },
        )

        assert create_response.status_code == 201

        trip_id = create_response.json()["id"]

        calls_before_update = mock_post.call_count

        update_response = client.put(
            f"/trips/{trip_id}",
            headers=auth_headers,
            json={
                "title": "오사카 여행 수정",
                "destination": "오사카",
                "start_date": "2026-10-20",
                "end_date": "2026-10-22",
            },
        )

    assert update_response.status_code == 200

    assert mock_post.call_count == calls_before_update