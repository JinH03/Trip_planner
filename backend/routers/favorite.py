
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.dependencies.auth import get_current_user
from backend.models import User
from backend.schemas.favorite import (
    FavoriteCreate,
    FavoriteResponse,
)
from backend.services.favorite import (
    create_favorite_service,
    delete_favorite_service,
    get_favorites_service,
)


router = APIRouter(
    prefix="/favorites",
    tags=["favorites"],
)


@router.post(
    "",
    response_model=FavoriteResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_favorite(
    favorite_data: FavoriteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_favorite_service(
        db=db,
        user_id=current_user.id,
        place_id=favorite_data.place_id,
    )


@router.get(
    "",
    response_model=list[FavoriteResponse],
)
def get_favorites(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_favorites_service(
        db=db,
        user_id=current_user.id,
    )


@router.delete(
    "/{place_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_favorite(
    place_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    delete_favorite_service(
        db=db,
        user_id=current_user.id,
        place_id=place_id,
    )
