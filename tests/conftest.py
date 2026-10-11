import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database import Base, get_db
from backend.main import app
from backend.models import User
from backend.services.auth import create_access_token


TEST_DATABASE_URL = "sqlite://"


engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={
        "check_same_thread": False,
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


def create_test_user(
    db,
    email: str,
) -> User:
    user = User(
        email=email,
        password_hash=None,
        email_verified=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def create_auth_headers(
    db,
    email: str,
) -> dict:
    user = create_test_user(
        db=db,
        email=email,
    )

    access_token = create_access_token(
        user.id
    )

    return {
        "Authorization": f"Bearer {access_token}"
    }


@pytest.fixture
def auth_headers(db):
    return create_auth_headers(
        db=db,
        email="test@example.com",
    )


@pytest.fixture
def second_auth_headers(db):
    return create_auth_headers(
        db=db,
        email="second@example.com",
    )