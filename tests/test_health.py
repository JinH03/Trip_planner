
from unittest.mock import MagicMock, patch

from sqlalchemy.exc import OperationalError


def test_liveness_check(client):
    response = client.get("/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_readiness_all_healthy(client):
    mock_connection = MagicMock()
    mock_engine = MagicMock()

    mock_engine.connect.return_value.__enter__.return_value = (
        mock_connection
    )

    mock_redis = MagicMock()
    mock_redis.ping.return_value = True

    with (
        patch("backend.routers.health.engine", mock_engine),
        patch(
            "backend.routers.health.get_redis_client",
            return_value=mock_redis,
        ),
    ):
        response = client.get("/health/ready")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "services": {
            "database": "up",
            "redis": "up",
        },
    }

    mock_connection.execute.assert_called_once()
    mock_redis.ping.assert_called_once()


def test_readiness_database_down(client):
    mock_engine = MagicMock()

    mock_engine.connect.side_effect = OperationalError(
        "SELECT 1",
        {},
        Exception("Database connection failed"),
    )

    mock_redis = MagicMock()
    mock_redis.ping.return_value = True

    with (
        patch("backend.routers.health.engine", mock_engine),
        patch(
            "backend.routers.health.get_redis_client",
            return_value=mock_redis,
        ),
    ):
        response = client.get("/health/ready")

    assert response.status_code == 503
    assert response.json() == {
        "status": "degraded",
        "services": {
            "database": "down",
            "redis": "up",
        },
    }


def test_readiness_redis_down(client):
    mock_engine = MagicMock()

    mock_redis = MagicMock()
    mock_redis.ping.side_effect = ConnectionError(
        "Redis connection failed"
    )

    with (
        patch("backend.routers.health.engine", mock_engine),
        patch(
            "backend.routers.health.get_redis_client",
            return_value=mock_redis,
        ),
    ):
        response = client.get("/health/ready")

    assert response.status_code == 503
    assert response.json() == {
        "status": "degraded",
        "services": {
            "database": "up",
            "redis": "down",
        },
    }


def test_readiness_all_services_down(client):
    mock_engine = MagicMock()

    mock_engine.connect.side_effect = OperationalError(
        "SELECT 1",
        {},
        Exception("Database connection failed"),
    )

    mock_redis = MagicMock()
    mock_redis.ping.side_effect = ConnectionError(
        "Redis connection failed"
    )

    with (
        patch("backend.routers.health.engine", mock_engine),
        patch(
            "backend.routers.health.get_redis_client",
            return_value=mock_redis,
        ),
    ):
        response = client.get("/health/ready")

    assert response.status_code == 503
    assert response.json() == {
        "status": "degraded",
        "services": {
            "database": "down",
            "redis": "down",
        },
    }


def test_health_check_requires_no_auth(client):
    live_response = client.get("/health/live")

    mock_engine = MagicMock()
    mock_redis = MagicMock()

    with (
        patch("backend.routers.health.engine", mock_engine),
        patch(
            "backend.routers.health.get_redis_client",
            return_value=mock_redis,
        ),
    ):
        ready_response = client.get("/health/ready")

    assert live_response.status_code == 200
    assert ready_response.status_code == 200
