import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from backend.database import Base, get_db
from backend.main import app
from backend.models import User


TEST_DATABASE_URL = "sqlite://"


engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={
        "check_same_thread": False
    },
    poolclass=StaticPool,
)


TestingSessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


def override_get_db():
    db = TestingSessionLocal()

    try:
        yield db

    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def reset_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    yield

    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def db():
    database = TestingSessionLocal()

    try:
        yield database

    finally:
        database.close()


@pytest.fixture
def auth_headers(client, db):
    email = "test@example.com"
    password = "test1234"

    signup_response = client.post(
        "/users",
        json={
            "email": email,
            "password": password,
        },
    )

    assert signup_response.status_code in [200, 201]

    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    assert user is not None

    user.email_verified = True
    db.commit()

    login_response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert login_response.status_code == 200

    access_token = login_response.json()["access_token"]

    return {
        "Authorization": f"Bearer {access_token}"
    }

@pytest.fixture
def second_auth_headers(client, db):
    email = "second@example.com"
    password = "test1234"

    signup_response = client.post(
        "/users",
        json={
            "email": email,
            "password": password,
        },
    )

    assert signup_response.status_code in [200, 201]

    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    assert user is not None

    user.email_verified = True
    db.commit()

    login_response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert login_response.status_code == 200

    access_token = login_response.json()["access_token"]

    return {
        "Authorization": f"Bearer {access_token}"
    }

@pytest.fixture
def second_auth_headers(client, db):
    email = "second@example.com"
    password = "test1234"

    signup_response = client.post(
        "/users",
        json={
            "email": email,
            "password": password,
        },
    )

    assert signup_response.status_code in [200, 201]

    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    assert user is not None

    user.email_verified = True
    db.commit()

    login_response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert login_response.status_code == 200

    access_token = login_response.json()["access_token"]

    return {
        "Authorization": f"Bearer {access_token}"
    }