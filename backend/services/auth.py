
import os
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from jose import jwt
from sqlalchemy.orm import Session

from backend.config import require_env
from backend.models import User
from backend.services.user import verify_password

load_dotenv()

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30")
)


def authenticate_user(
    email: str,
    password: str,
    db: Session,
):
    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if not user:
        return None

    if not user.password_hash:
        return None

    if not verify_password(
        password,
        user.password_hash,
    ):
        return None

    return user


def create_access_token(user_id: int) -> str:
    # 기존 모듈 변수와 테스트 호환성 유지
    secret_key = JWT_SECRET_KEY

    # 비밀키가 없거나 공백이면 공통 검증 함수 사용
    if not secret_key or not secret_key.strip():
        secret_key = require_env("JWT_SECRET_KEY")

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "exp": expire,
    }

    return jwt.encode(
        payload,
        secret_key,
        algorithm=JWT_ALGORITHM,
    )
