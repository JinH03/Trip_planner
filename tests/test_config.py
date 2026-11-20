
import pytest

from backend.config import (
    ConfigError,
    require_env,
    validate_environment,
)


def test_require_env_returns_value(monkeypatch):
    monkeypatch.setenv("TEST_CONFIG_KEY", "hello")

    assert require_env("TEST_CONFIG_KEY") == "hello"


def test_require_env_missing(monkeypatch):
    monkeypatch.delenv("TEST_CONFIG_KEY", raising=False)

    with pytest.raises(
        ConfigError,
        match="Missing required environment variable: TEST_CONFIG_KEY",
    ):
        require_env("TEST_CONFIG_KEY")


def test_require_env_empty(monkeypatch):
    monkeypatch.setenv("TEST_CONFIG_KEY", "")

    with pytest.raises(ConfigError):
        require_env("TEST_CONFIG_KEY")


def test_require_env_whitespace(monkeypatch):
    monkeypatch.setenv("TEST_CONFIG_KEY", "   ")

    with pytest.raises(ConfigError):
        require_env("TEST_CONFIG_KEY")


def test_validate_environment_success(monkeypatch):
    monkeypatch.setenv(
        "DATABASE_URL",
        "sqlite:///./test.db",
    )
    monkeypatch.setenv(
        "JWT_SECRET_KEY",
        "test-only-secret",
    )

    validate_environment()


def test_validate_environment_missing_jwt(monkeypatch):
    monkeypatch.setenv(
        "DATABASE_URL",
        "sqlite:///./test.db",
    )
    monkeypatch.delenv("JWT_SECRET_KEY", raising=False)

    with pytest.raises(
        ConfigError,
        match="JWT_SECRET_KEY",
    ):
        validate_environment()


def test_config_error_does_not_expose_secret(monkeypatch):
    secret = "super-secret-value"
    monkeypatch.setenv("TEST_CONFIG_KEY", secret)

    assert require_env("TEST_CONFIG_KEY") == secret

    monkeypatch.setenv("TEST_CONFIG_KEY", " ")

    with pytest.raises(ConfigError) as error:
        require_env("TEST_CONFIG_KEY")

    assert secret not in str(error.value)


def test_create_access_token_missing_secret(monkeypatch):
    from backend.services import auth as auth_service

    monkeypatch.setattr(
        auth_service,
        "JWT_SECRET_KEY",
        None,
    )
    monkeypatch.delenv("JWT_SECRET_KEY", raising=False)

    with pytest.raises(
        ConfigError,
        match="JWT_SECRET_KEY",
    ):
        auth_service.create_access_token(user_id=1)


def test_create_access_token_with_secret(monkeypatch):
    import jwt
    from backend.services import auth as auth_service

    secret = "day27-test-only-secret"

    monkeypatch.setattr(
        auth_service,
        "JWT_SECRET_KEY",
        secret,
    )

    token = auth_service.create_access_token(user_id=1)

    payload = jwt.decode(
        token,
        secret,
        algorithms=[auth_service.JWT_ALGORITHM],
    )

    assert payload["sub"] == "1"


def test_database_url_success(monkeypatch):
    monkeypatch.setenv(
        "DATABASE_URL",
        "sqlite:///./test.db",
    )

    assert (
        require_env("DATABASE_URL")
        == "sqlite:///./test.db"
    )


def test_database_url_missing(monkeypatch):
    monkeypatch.delenv(
        "DATABASE_URL",
        raising=False,
    )

    with pytest.raises(
        ConfigError,
        match="DATABASE_URL",
    ):
        require_env("DATABASE_URL")

def test_pyjwt_rejects_expired_token():
    import jwt
    from datetime import datetime, timedelta, timezone

    secret = "day30-test-secret"

    expired = datetime.now(timezone.utc) - timedelta(
        minutes=1
    )

    token = jwt.encode(
        {
            "sub": "1",
            "exp": expired,
        },
        secret,
        algorithm="HS256",
    )

    with pytest.raises(jwt.ExpiredSignatureError):
        jwt.decode(
            token,
            secret,
            algorithms=["HS256"],
        )


def test_pyjwt_rejects_wrong_algorithm():
    import jwt

    secret = "day30-test-secret"

    token = jwt.encode(
        {"sub": "1"},
        secret,
        algorithm="HS384",
    )

    with pytest.raises(jwt.InvalidAlgorithmError):
        jwt.decode(
            token,
            secret,
            algorithms=["HS256"],
        )
