from fastapi import APIRouter, Depends, HTTPException
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