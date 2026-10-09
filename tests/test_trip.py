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