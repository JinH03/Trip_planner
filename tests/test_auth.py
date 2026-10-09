from backend.models import User


def test_login_and_access_trips(
    client,
    db,
):
    signup_response = client.post(
        "/users",
        json={
            "email": "test@example.com",
            "password": "test1234",
        },
    )

    assert signup_response.status_code in [200, 201]
    user = (
        db.query(User)
        .filter(
            User.email == "test@example.com"
        )
        .first()
    )

    assert user is not None
    user.email_verified = True

    db.commit()
    login_response = client.post(
        "/auth/login",
        json={
            "email": "test@example.com",
            "password": "test1234",
        },
    )

    assert login_response.status_code == 200
    data = login_response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"

    access_token = data["access_token"]
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    trips_response = client.get(
        "/trips",
        headers=headers,
    )

    assert trips_response.status_code == 200