def create_trip_and_get_day_id(
    client,
    auth_headers,
):
    response = client.post(
        "/trips",
        headers=auth_headers,
        json={
            "title": "오사카 여행",
            "destination": "오사카",
            "start_date": "2026-10-10",
            "end_date": "2026-10-11",
        },
    )

    assert response.status_code == 201

    trip_id = response.json()["id"]

    detail_response = client.get(
        f"/trips/{trip_id}/detail",
        headers=auth_headers,
    )

    assert detail_response.status_code == 200

    days = detail_response.json()["days"]

    return days[0]["id"]

def test_create_schedule(
    client,
    auth_headers,
):
    trip_day_id = create_trip_and_get_day_id(
        client,
        auth_headers,
    )

    response = client.post(
        f"/trip-days/{trip_day_id}/schedules",
        headers=auth_headers,
        json={
            "title": "오사카성",
            "start_time": "10:00:00",
            "place": "오사카성",
            "memo": "사진 찍기",
            "order_index": 0,
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["title"] == "오사카성"
    assert data["place"] == "오사카성"
    assert data["memo"] == "사진 찍기"
    assert data["order_index"] == 0


def test_update_schedule(
    client,
    auth_headers,
):
    trip_day_id = create_trip_and_get_day_id(
        client,
        auth_headers,
    )

    create_response = client.post(
        f"/trip-days/{trip_day_id}/schedules",
        headers=auth_headers,
        json={
            "title": "오사카성",
            "start_time": "10:00:00",
            "place": "오사카성",
            "memo": None,
            "order_index": 0,
        },
    )

    assert create_response.status_code == 201

    schedule_id = create_response.json()["id"]

    update_response = client.put(
        f"/trip-days/{trip_day_id}/schedules/{schedule_id}",
        headers=auth_headers,
        json={
            "title": "도톤보리",
            "start_time": "18:00:00",
            "place": "도톤보리",
            "memo": "저녁 먹기",
            "order_index": 1,
        },
    )

    assert update_response.status_code == 200

    data = update_response.json()

    assert data["title"] == "도톤보리"
    assert data["order_index"] == 1

def test_delete_schedule(
    client,
    auth_headers,
):
    trip_day_id = create_trip_and_get_day_id(
        client,
        auth_headers,
    )

    create_response = client.post(
        f"/trip-days/{trip_day_id}/schedules",
        headers=auth_headers,
        json={
            "title": "오사카성",
            "start_time": "10:00:00",
            "place": "오사카성",
            "memo": None,
            "order_index": 0,
        },
    )

    schedule_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/trip-days/{trip_day_id}/schedules/{schedule_id}",
        headers=auth_headers,
    )

    assert delete_response.status_code == 204

    get_response = client.get(
        f"/trip-days/{trip_day_id}/schedules/{schedule_id}",
        headers=auth_headers,
    )

    assert get_response.status_code == 404

def test_reorder_schedules(
    client,
    auth_headers,
):
    trip_day_id = create_trip_and_get_day_id(
        client,
        auth_headers,
    )

    first_response = client.post(
        f"/trip-days/{trip_day_id}/schedules",
        headers=auth_headers,
        json={
            "title": "첫 번째",
            "start_time": "10:00:00",
            "place": None,
            "memo": None,
            "order_index": 0,
        },
    )

    second_response = client.post(
        f"/trip-days/{trip_day_id}/schedules",
        headers=auth_headers,
        json={
            "title": "두 번째",
            "start_time": "11:00:00",
            "place": None,
            "memo": None,
            "order_index": 1,
        },
    )

    first_id = first_response.json()["id"]
    second_id = second_response.json()["id"]

    reorder_response = client.put(
        f"/trip-days/{trip_day_id}/schedules/reorder",
        headers=auth_headers,
        json={
            "schedules": [
                {
                    "schedule_id": first_id,
                    "order_index": 1,
                },
                {
                    "schedule_id": second_id,
                    "order_index": 0,
                },
            ]
        },
    )

    assert reorder_response.status_code == 200

    data = reorder_response.json()

    assert data[0]["id"] == second_id
    assert data[0]["order_index"] == 0

    assert data[1]["id"] == first_id
    assert data[1]["order_index"] == 1

def test_create_schedule_with_blank_title(
    client,
    auth_headers,
):
    trip_day_id = create_trip_and_get_day_id(
        client,
        auth_headers,
    )

    response = client.post(
        f"/trip-days/{trip_day_id}/schedules",
        headers=auth_headers,
        json={
            "title": "     ",
            "start_time": "10:00:00",
            "place": "오사카",
            "memo": None,
            "order_index": 0,
        },
    )

    assert response.status_code == 422

def test_create_schedule_with_negative_order_index(
    client,
    auth_headers,
):
    trip_day_id = create_trip_and_get_day_id(
        client,
        auth_headers,
    )

    response = client.post(
        f"/trip-days/{trip_day_id}/schedules",
        headers=auth_headers,
        json={
            "title": "오사카성",
            "start_time": "10:00:00",
            "place": "오사카",
            "memo": None,
            "order_index": -1,
        },
    )

    assert response.status_code == 422


def test_reorder_duplicate_schedule_id(
    client,
    auth_headers,
):
    trip_day_id = create_trip_and_get_day_id(
        client,
        auth_headers,
    )

    create_response = client.post(
        f"/trip-days/{trip_day_id}/schedules",
        headers=auth_headers,
        json={
            "title": "첫 번째",
            "start_time": "10:00:00",
            "place": None,
            "memo": None,
            "order_index": 0,
        },
    )

    schedule_id = create_response.json()["id"]

    response = client.put(
        f"/trip-days/{trip_day_id}/schedules/reorder",
        headers=auth_headers,
        json={
            "schedules": [
                {
                    "schedule_id": schedule_id,
                    "order_index": 0,
                },
                {
                    "schedule_id": schedule_id,
                    "order_index": 1,
                },
            ]
        },
    )

    assert response.status_code == 400

def test_reorder_duplicate_order_index(
    client,
    auth_headers,
):
    trip_day_id = create_trip_and_get_day_id(
        client,
        auth_headers,
    )

    first_response = client.post(
        f"/trip-days/{trip_day_id}/schedules",
        headers=auth_headers,
        json={
            "title": "첫 번째",
            "start_time": "10:00:00",
            "place": None,
            "memo": None,
            "order_index": 0,
        },
    )

    second_response = client.post(
        f"/trip-days/{trip_day_id}/schedules",
        headers=auth_headers,
        json={
            "title": "두 번째",
            "start_time": "11:00:00",
            "place": None,
            "memo": None,
            "order_index": 1,
        },
    )

    first_id = first_response.json()["id"]
    second_id = second_response.json()["id"]

    response = client.put(
        f"/trip-days/{trip_day_id}/schedules/reorder",
        headers=auth_headers,
        json={
            "schedules": [
                {
                    "schedule_id": first_id,
                    "order_index": 0,
                },
                {
                    "schedule_id": second_id,
                    "order_index": 0,
                },
            ]
        },
    )

    assert response.status_code == 400

def test_reorder_empty_schedules(
    client,
    auth_headers,
):
    trip_day_id = create_trip_and_get_day_id(
        client,
        auth_headers,
    )

    response = client.put(
        f"/trip-days/{trip_day_id}/schedules/reorder",
        headers=auth_headers,
        json={
            "schedules": []
        },
    )

    assert response.status_code == 422