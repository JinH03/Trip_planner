
import os

from dotenv import load_dotenv


load_dotenv()


class ConfigError(ValueError):
    """환경변수 설정 오류."""


def require_env(name: str) -> str:
    """
    필수 환경변수를 검사한다.

    값이 없거나 공백이면 오류를 발생시킨다.
    실제 설정값은 오류 메시지에 포함하지 않는다.
    """
    value = os.getenv(name)

    if not value or not value.strip():
        raise ConfigError(
            f"Missing required environment variable: {name}"
        )

    return value


def validate_environment() -> None:
    """
    핵심 서비스 실행에 필요한 환경변수 검증.

    SMTP 및 OAuth 관련 설정은 해당 기능에서
    별도로 검증할 수 있도록 제외한다.
    """
    required_variables = [
        "DATABASE_URL",
        "JWT_SECRET_KEY",
    ]

    for variable in required_variables:
        require_env(variable)
