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

def create_test_place(client):
    response = client.post(
        "/places",
        json={
            "name": "오사카성",
            "address": "1-1 Osakajo, Chuo Ward, Osaka",
            "latitude": 34.6873,
            "longitude": 135.5262,
            "category": "관광지",
            "external_place_id": "test-osaka-castle",
        },
    )

    assert response.status_code == 201

    return response.json()
def test_create_schedule_with_place(
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

    detail_response = client.get(
        f"/trips/{trip_id}/detail",
        headers=auth_headers,
    )

    assert detail_response.status_code == 200

    trip_day_id = detail_response.json()["days"][0]["id"]

    place = create_test_place(client)

    response = client.post(
        f"/trip-days/{trip_day_id}/schedules",
        headers=auth_headers,
        json={
            "title": "오사카성 관광",
            "start_time": "10:00:00",
            "place": "오사카성",
            "place_id": place["id"],
            "memo": "사진 찍기",
            "order_index": 0,
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["title"] == "오사카성 관광"
    assert data["place_id"] == place["id"]

    assert data["place_info"] is not None
    assert data["place_info"]["id"] == place["id"]
    assert data["place_info"]["name"] == "오사카성"
def test_create_schedule_with_invalid_place_id(
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

    detail_response = client.get(
        f"/trips/{trip_id}/detail",
        headers=auth_headers,
    )

    trip_day_id = detail_response.json()["days"][0]["id"]

    response = client.post(
        f"/trip-days/{trip_day_id}/schedules",
        headers=auth_headers,
        json={
            "title": "없는 장소 테스트",
            "start_time": "10:00:00",
            "place": "없는 장소",
            "place_id": 999999,
            "memo": None,
            "order_index": 0,
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid place_id"

def test_trip_detail_contains_schedule_place_info(
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

    detail_response = client.get(
        f"/trips/{trip_id}/detail",
        headers=auth_headers,
    )

    assert detail_response.status_code == 200

    trip_day_id = detail_response.json()["days"][0]["id"]

    place = create_test_place(client)

    schedule_response = client.post(
        f"/trip-days/{trip_day_id}/schedules",
        headers=auth_headers,
        json={
            "title": "오사카성 관광",
            "start_time": "10:00:00",
            "place": "오사카성",
            "place_id": place["id"],
            "memo": None,
            "order_index": 0,
        },
    )

    assert schedule_response.status_code == 201

    detail_response = client.get(
        f"/trips/{trip_id}/detail",
        headers=auth_headers,
    )

    assert detail_response.status_code == 200

    data = detail_response.json()

    schedule = data["days"][0]["schedules"][0]

    assert schedule["place_id"] == place["id"]

    assert schedule["place_info"] is not None
    assert schedule["place_info"]["id"] == place["id"]
    assert schedule["place_info"]["name"] == "오사카성"

def create_day15_trip_day(client, auth_headers):
    trip_response = client.post(
        "/trips",
        headers=auth_headers,
        json={
            "title": "오사카 여행",
            "destination": "오사카",
            "start_date": "2026-11-01",
            "end_date": "2026-11-02",
        },
    )

    assert trip_response.status_code == 201

    trip_id = trip_response.json()["id"]

    detail_response = client.get(
        f"/trips/{trip_id}/detail",
        headers=auth_headers,
    )

    assert detail_response.status_code == 200

    return detail_response.json()["days"][0]["id"]


def create_day15_schedule(
    client,
    auth_headers,
    trip_day_id,
    title,
    start_time,
    end_time,
    order_index=0,
):
    return client.post(
        f"/trip-days/{trip_day_id}/schedules",
        headers=auth_headers,
        json={
            "title": title,
            "start_time": start_time,
            "end_time": end_time,
            "order_index": order_index,
        },
    )


def test_create_schedule_with_valid_time_range(
    client,
    auth_headers,
):
    trip_day_id = create_day15_trip_day(
        client, auth_headers
    )

    response = create_day15_schedule(
        client,
        auth_headers,
        trip_day_id,
        "오사카성 관광",
        "09:00",
        "11:00",
    )

    assert response.status_code == 201
    assert response.json()["start_time"] == "09:00:00"
    assert response.json()["end_time"] == "11:00:00"


def test_create_schedule_with_conflicting_time(
    client,
    auth_headers,
):
    trip_day_id = create_day15_trip_day(
        client, auth_headers
    )

    first_response = create_day15_schedule(
        client,
        auth_headers,
        trip_day_id,
        "오사카성 관광",
        "09:00",
        "11:00",
    )

    assert first_response.status_code == 201

    second_response = create_day15_schedule(
        client,
        auth_headers,
        trip_day_id,
        "점심 식사",
        "10:30",
        "12:00",
        order_index=1,
    )

    assert second_response.status_code == 400
    assert (
        second_response.json()["detail"]
        == "Schedule time conflicts with an existing schedule"
    )


def test_create_schedule_without_conflicting_time(
    client,
    auth_headers,
):
    trip_day_id = create_day15_trip_day(
        client, auth_headers
    )

    first_response = create_day15_schedule(
        client,
        auth_headers,
        trip_day_id,
        "오사카성 관광",
        "09:00",
        "11:00",
    )

    assert first_response.status_code == 201

    second_response = create_day15_schedule(
        client,
        auth_headers,
        trip_day_id,
        "도톤보리 관광",
        "13:00",
        "15:00",
        order_index=1,
    )

    assert second_response.status_code == 201


def test_create_schedule_with_adjacent_time(
    client,
    auth_headers,
):
    trip_day_id = create_day15_trip_day(
        client, auth_headers
    )

    first_response = create_day15_schedule(
        client,
        auth_headers,
        trip_day_id,
        "오사카성 관광",
        "09:00",
        "11:00",
    )

    assert first_response.status_code == 201

    second_response = create_day15_schedule(
        client,
        auth_headers,
        trip_day_id,
        "점심 식사",
        "11:00",
        "12:00",
        order_index=1,
    )

    assert second_response.status_code == 201


def test_create_schedule_with_invalid_time_range(
    client,
    auth_headers,
):
    trip_day_id = create_day15_trip_day(
        client, auth_headers
    )

    response = create_day15_schedule(
        client,
        auth_headers,
        trip_day_id,
        "잘못된 일정",
        "15:00",
        "13:00",
    )

    assert response.status_code == 422


def test_update_schedule_with_conflicting_time(
    client,
    auth_headers,
):
    trip_day_id = create_day15_trip_day(
        client, auth_headers
    )

    first_response = create_day15_schedule(
        client,
        auth_headers,
        trip_day_id,
        "오사카성 관광",
        "09:00",
        "11:00",
    )

    second_response = create_day15_schedule(
        client,
        auth_headers,
        trip_day_id,
        "도톤보리 관광",
        "13:00",
        "15:00",
        order_index=1,
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 201

    schedule_id = second_response.json()["id"]

    update_response = client.put(
        f"/trip-days/{trip_day_id}/schedules/{schedule_id}",
        headers=auth_headers,
        json={
            "title": "도톤보리 관광 수정",
            "start_time": "10:30",
            "end_time": "12:00",
            "order_index": 1,
        },
    )

    assert update_response.status_code == 400


def test_update_schedule_excludes_itself_from_conflict(
    client,
    auth_headers,
):
    trip_day_id = create_day15_trip_day(
        client, auth_headers
    )

    create_response = create_day15_schedule(
        client,
        auth_headers,
        trip_day_id,
        "오사카성 관광",
        "09:00",
        "11:00",
    )

    assert create_response.status_code == 201

    schedule_id = create_response.json()["id"]

    update_response = client.put(
        f"/trip-days/{trip_day_id}/schedules/{schedule_id}",
        headers=auth_headers,
        json={
            "title": "오사카성 관광 수정",
            "start_time": "09:00",
            "end_time": "11:00",
            "order_index": 0,
        },
    )

    assert update_response.status_code == 200

def test_schedule_same_time_on_different_days(
    client,
    auth_headers,
):
    trip_response = client.post(
        "/trips",
        headers=auth_headers,
        json={
            "title": "오사카 여행",
            "destination": "오사카",
            "start_date": "2026-11-01",
            "end_date": "2026-11-02",
        },
    )

    assert trip_response.status_code == 201

    trip_id = trip_response.json()["id"]

    detail_response = client.get(
        f"/trips/{trip_id}/detail",
        headers=auth_headers,
    )

    assert detail_response.status_code == 200

    days = detail_response.json()["days"]

    day1_id = days[0]["id"]
    day2_id = days[1]["id"]

    first_response = create_day15_schedule(
        client,
        auth_headers,
        day1_id,
        "오사카성 관광",
        "09:00",
        "11:00",
    )

    second_response = create_day15_schedule(
        client,
        auth_headers,
        day2_id,
        "도톤보리 관광",
        "09:00",
        "11:00",
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 201

def test_schedule_without_end_time(
    client,
    auth_headers,
):
    trip_day_id = create_day15_trip_day(
        client,
        auth_headers,
    )

    first_response = create_day15_schedule(
        client,
        auth_headers,
        trip_day_id,
        "종료 시간 없는 기존 일정",
        "09:00",
        None,
    )

    assert first_response.status_code == 201
    assert first_response.json()["end_time"] is None

    second_response = create_day15_schedule(
        client,
        auth_headers,
        trip_day_id,
        "새 일정",
        "09:30",
        "11:00",
        order_index=1,
    )

    assert second_response.status_code == 201