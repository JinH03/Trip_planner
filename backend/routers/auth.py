import secrets

from fastapi.responses import RedirectResponse

from backend.models import SocialAccount
from backend.services.google_oauth import (
    get_google_access_token,
    get_google_login_url,
    get_google_user_info,
)
from backend.services.kakao_oauth import (
    get_kakao_login_url,
    get_kakao_access_token,
    get_kakao_user_info,
)
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import User
from backend.services.email_verification import verify_code
from backend.schemas.auth import LoginRequest, TokenResponse
from backend.services.auth import (
    authenticate_user,
    create_access_token,
)

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

class VerifyEmailRequest(BaseModel):
    email: EmailStr
    code: str


@router.post("/verify-email")
def verify_email(
    request: VerifyEmailRequest,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.email_verified:
        return {"message": "Email already verified"}
    verified = verify_code(user.id, request.code, db)
    if not verified:
        raise HTTPException(status_code=400, detail="Invalid or expired verification code")
    user.email_verified = True
    db.commit()
    return {"message": "Email verified successfully"}

@router.post("/login", response_model=TokenResponse)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db),
):
    user = authenticate_user(
        request.email,
        request.password,
        db,
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    if not user.email_verified:
        raise HTTPException(
            status_code=403,
            detail="Email is not verified",
        )

    access_token = create_access_token(
        user.id,
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
    )

@router.get("/google/login")
def google_login():
    state = secrets.token_urlsafe(32)

    login_url = get_google_login_url(state)

    return RedirectResponse(login_url)
@router.get("/google/callback")
def google_callback(
    code: str,
    state: str,
    db: Session = Depends(get_db),
):
    access_token = get_google_access_token(code)

    google_user = get_google_user_info(access_token)

    provider_user_id = google_user["sub"]
    email = google_user["email"]

    social_account = (
        db.query(SocialAccount)
        .filter(
            SocialAccount.provider == "google",
            SocialAccount.provider_user_id == provider_user_id,
        )
        .first()
    )

    if social_account:
        user = social_account.user

    else:
        user = (
            db.query(User)
            .filter(User.email == email)
            .first()
        )

        if not user:
            user = User(
                email=email,
                password_hash=None,
                email_verified=True,
            )

            db.add(user)
            db.commit()
            db.refresh(user)

        social_account = SocialAccount(
            user_id=user.id,
            provider="google",
            provider_user_id=provider_user_id,
        )

        db.add(social_account)
        db.commit()

    token = create_access_token(user.id)

    return {
        "access_token": token,
        "token_type": "bearer",
    }

@router.get("/kakao/login")
def kakao_login():
    login_url = get_kakao_login_url()

    return RedirectResponse(login_url)
@router.get("/kakao/callback")
def kakao_callback(
    code: str,
    db: Session = Depends(get_db),
):
    access_token = get_kakao_access_token(code)

    kakao_user = get_kakao_user_info(access_token)

    provider_user_id = str(kakao_user["id"])

    social_account = (
        db.query(SocialAccount)
        .filter(
            SocialAccount.provider == "kakao",
            SocialAccount.provider_user_id == provider_user_id,
        )
        .first()
    )

    if social_account:
        user = social_account.user

    else:
        user = User(
            email=None,
            password_hash=None,
            email_verified=False,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        social_account = SocialAccount(
            user_id=user.id,
            provider="kakao",
            provider_user_id=provider_user_id,
        )

        db.add(social_account)
        db.commit()

    token = create_access_token(user.id)

    return {
        "access_token": token,
        "token_type": "bearer",
    }