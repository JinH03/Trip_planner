import bcrypt

from sqlalchemy.orm import Session

from backend.models import User
from backend.services.email_verification import create_verification_code


def hash_password(password: str) -> str:
    password_bytes = password.encode("utf-8")

    if len(password_bytes) > 72:
        raise ValueError("Password must be 72 bytes or less")

    return bcrypt.hashpw(
        password_bytes,
        bcrypt.gensalt(),
    ).decode("utf-8")


def verify_password(
    password: str,
    password_hash: str,
) -> bool:
    return bcrypt.checkpw(
        password.encode("utf-8"),
        password_hash.encode("utf-8"),
    )


def create_user(
    email: str,
    password: str,
    db: Session,
):
    existing_user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if existing_user:
        return None

    password_hash = hash_password(password)

    new_user = User(
        email=email,
        password_hash=password_hash,
        email_verified=False,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    code = create_verification_code(
        new_user.id,
        db,
    )

    # 현재는 실제 이메일 발송 전이므로 테스트용
    print(
        f"[EMAIL VERIFICATION] "
        f"{email} -> {code}"
    )

    return new_user