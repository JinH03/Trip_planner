from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import EmailStr
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import User
from backend.schemas.user import UserCreate, UserResponse
from backend.services.user import create_user
from backend.services.email_verification import create_verification_code
from backend.services.email import send_verification_email
from backend.dependencies.auth import get_current_user

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_user(
    user: UserCreate,
    db: Session = Depends(get_db),
):
    new_user = create_user(
        user.email,
        user.password,
        db,
    )

    if new_user is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    verification_code = create_verification_code(
        new_user.id,
        db,
    )

    send_verification_email(
        new_user.email,
        verification_code,
    )

    print(
        f"[EMAIL VERIFICATION] "
        f"{new_user.email} -> {verification_code}"
    )

    return new_user


@router.get(
    "/me",
    response_model=UserResponse,
)
def get_me(
    current_user: User = Depends(get_current_user),
):
    return current_user