def test_create_place(client):
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

    data = response.json()

    assert data["id"] is not None
    assert data["name"] == "오사카성"
    assert data["address"] == "1-1 Osakajo, Chuo Ward, Osaka"
    assert data["latitude"] == 34.6873
    assert data["longitude"] == 135.5262
    assert data["category"] == "관광지"
    assert data["external_place_id"] == "test-osaka-castle"


def test_create_duplicate_place_returns_existing_place(client):
    place_data = {
        "name": "오사카성",
        "address": "1-1 Osakajo, Chuo Ward, Osaka",
        "latitude": 34.6873,
        "longitude": 135.5262,
        "category": "관광지",
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


def test_search_places(client):
    response = client.get(
        "/places/search",
        params={
            "query": "오사카",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) >= 1
    assert data[0]["name"] == "오사카성"


def test_search_places_dotonbori(client):
    response = client.get(
        "/places/search",
        params={
            "query": "도톤",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) >= 1
    assert data[0]["name"] == "도톤보리"