
import pytest


def create_test_place(client):
    response = client.post(
        "/places",
        json={
            "name": "오사카성",
            "address": "Osaka, Japan",
            "latitude": 34.6873,
            "longitude": 135.5262,
            "category": "castle",
            "external_place_id": "day18-osaka-castle",
        },
    )

    assert response.status_code == 201
    return response.json()["id"]


def test_create_favorite(client, auth_headers):
    place_id = create_test_place(client)

    response = client.post(
        "/favorites",
        headers=auth_headers,
        json={"place_id": place_id},
    )

    assert response.status_code == 201

    data = response.json()
    assert data["place_id"] == place_id
    assert data["place"]["name"] == "오사카성"


def test_get_favorites(client, auth_headers):
    place_id = create_test_place(client)

    client.post(
        "/favorites",
        headers=auth_headers,
        json={"place_id": place_id},
    )

    response = client.get(
        "/favorites",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["place_id"] == place_id


def test_duplicate_favorite(client, auth_headers):
    place_id = create_test_place(client)

    first = client.post(
        "/favorites",
        headers=auth_headers,
        json={"place_id": place_id},
    )

    second = client.post(
        "/favorites",
        headers=auth_headers,
        json={"place_id": place_id},
    )

    assert first.status_code == 201
    assert second.status_code == 409


def test_delete_favorite(client, auth_headers):
    place_id = create_test_place(client)

    client.post(
        "/favorites",
        headers=auth_headers,
        json={"place_id": place_id},
    )

    response = client.delete(
        f"/favorites/{place_id}",
        headers=auth_headers,
    )

    assert response.status_code == 204

    favorites = client.get(
        "/favorites",
        headers=auth_headers,
    )

    assert favorites.status_code == 200
    assert favorites.json() == []


def test_delete_nonexistent_favorite(client, auth_headers):
    response = client.delete(
        "/favorites/99999",
        headers=auth_headers,
    )

    assert response.status_code == 404


def test_favorite_invalid_place(client, auth_headers):
    response = client.post(
        "/favorites",
        headers=auth_headers,
        json={"place_id": 99999},
    )

    assert response.status_code == 404


def test_favorite_invalid_place_id_validation(
    client,
    auth_headers,
):
    response = client.post(
        "/favorites",
        headers=auth_headers,
        json={"place_id": -1},
    )

    assert response.status_code == 422


def test_favorite_requires_auth(client):
    response = client.get("/favorites")

    assert response.status_code == 401


def test_favorite_user_isolation(
    client,
    auth_headers,
    second_auth_headers,
):
    place_id = create_test_place(client)

    first = client.post(
        "/favorites",
        headers=auth_headers,
        json={"place_id": place_id},
    )

    assert first.status_code == 201

    # 다른 사용자는 첫 번째 사용자의 즐겨찾기를 볼 수 없음
    second_user_list = client.get(
        "/favorites",
        headers=second_auth_headers,
    )

    assert second_user_list.status_code == 200
    assert second_user_list.json() == []

    # 다른 사용자가 삭제하려 해도 자신의 즐겨찾기가 아니므로 404
    delete_response = client.delete(
        f"/favorites/{place_id}",
        headers=second_auth_headers,
    )

    assert delete_response.status_code == 404

    # 원래 사용자의 즐겨찾기는 그대로 남아야 함
    first_user_list = client.get(
        "/favorites",
        headers=auth_headers,
    )

    assert len(first_user_list.json()) == 1


def test_two_users_can_favorite_same_place(
    client,
    auth_headers,
    second_auth_headers,
):
    place_id = create_test_place(client)

    first = client.post(
        "/favorites",
        headers=auth_headers,
        json={"place_id": place_id},
    )

    second = client.post(
        "/favorites",
        headers=second_auth_headers,
        json={"place_id": place_id},
    )

    assert first.status_code == 201
    assert second.status_code == 201
