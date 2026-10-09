def test_other_user_cannot_get_trip(
    client,
    auth_headers,
    second_auth_headers,
):
    # User A가 Trip 생성
    create_response = client.post(
        "/trips",
        headers=auth_headers,
        json={
            "title": "오사카 여행",
            "destination": "오사카",
            "start_date": "2026-10-10",
            "end_date": "2026-10-12",
        },
    )

    assert create_response.status_code == 201

    trip_id = create_response.json()["id"]

    # User B가 접근
    response = client.get(
        f"/trips/{trip_id}",
        headers=second_auth_headers,
    )

    assert response.status_code == 404

def test_other_user_cannot_update_trip(
    client,
    auth_headers,
    second_auth_headers,
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

    trip_id = create_response.json()["id"]

    response = client.put(
        f"/trips/{trip_id}",
        headers=second_auth_headers,
        json={
            "title": "해킹 시도",
            "destination": "서울",
            "start_date": "2026-10-10",
            "end_date": "2026-10-11",
        },
    )

    assert response.status_code == 404

def test_other_user_cannot_delete_trip(
    client,
    auth_headers,
    second_auth_headers,
):
    create_response = client.post(
        "/trips",
        headers=auth_headers,
        json={
            "title": "제주 여행",
            "destination": "제주",
            "start_date": "2026-10-10",
            "end_date": "2026-10-11",
        },
    )

    trip_id = create_response.json()["id"]

    response = client.delete(
        f"/trips/{trip_id}",
        headers=second_auth_headers,
    )

    assert response.status_code == 404

def test_other_user_cannot_get_schedule(
    client,
    auth_headers,
    second_auth_headers,
):
    # User A가 Trip 생성
    trip_response = client.post(
        "/trips",
        headers=auth_headers,
        json={
            "title": "도쿄 여행",
            "destination": "도쿄",
            "start_date": "2026-10-10",
            "end_date": "2026-10-11",
        },
    )

    trip_id = trip_response.json()["id"]

    # TripDay 조회
    detail_response = client.get(
        f"/trips/{trip_id}/detail",
        headers=auth_headers,
    )

    trip_day_id = detail_response.json()["days"][0]["id"]

    # User A가 Schedule 생성
    schedule_response = client.post(
        f"/trip-days/{trip_day_id}/schedules",
        headers=auth_headers,
        json={
            "title": "시부야",
            "start_time": "10:00:00",
            "place": "시부야",
            "memo": None,
            "order_index": 0,
        },
    )

    schedule_id = schedule_response.json()["id"]

    # User B가 접근
    response = client.get(
        f"/trip-days/{trip_day_id}/schedules/{schedule_id}",
        headers=second_auth_headers,
    )

    assert response.status_code == 404