import hashlib
import secrets
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from backend.models import EmailVerification


def create_verification_code(
    user_id: int,
    db: Session,
) -> str:
    # 6자리 인증번호 생성
    code = f"{secrets.randbelow(1_000_000):06d}"

    # DB에는 인증번호 자체가 아니라 해시만 저장
    code_hash = hashlib.sha256(
        code.encode("utf-8")
    ).hexdigest()

    verification = EmailVerification(
        user_id=user_id,
        code_hash=code_hash,
        expires_at=datetime.utcnow() + timedelta(minutes=10),
    )

    db.add(verification)
    db.commit()

    return code


def verify_code(
    user_id: int,
    code: str,
    db: Session,
) -> bool:
    code_hash = hashlib.sha256(
        code.encode("utf-8")
    ).hexdigest()

    verification = (
        db.query(EmailVerification)
        .filter(
            EmailVerification.user_id == user_id,
            EmailVerification.code_hash == code_hash,
            EmailVerification.verified_at.is_(None),
        )
        .order_by(
            EmailVerification.created_at.desc()
        )
        .first()
    )

    if not verification:
        return False

    # 10분 만료
    if verification.expires_at < datetime.utcnow():
        return False

    verification.verified_at = datetime.utcnow()

    db.commit()

    return True