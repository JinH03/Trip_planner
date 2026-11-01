
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from backend.models import FavoritePlace, Place


def create_favorite_service(
    db: Session,
    user_id: int,
    place_id: int,
) -> FavoritePlace:
    place = db.query(Place).filter(
        Place.id == place_id
    ).first()

    if not place:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Place not found",
        )

    existing = db.query(FavoritePlace).filter(
        FavoritePlace.user_id == user_id,
        FavoritePlace.place_id == place_id,
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Place already favorited",
        )

    favorite = FavoritePlace(
        user_id=user_id,
        place_id=place_id,
    )

    try:
        db.add(favorite)
        db.commit()
        db.refresh(favorite)
        return favorite

    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Place already favorited",
        ) from exc

    except Exception:
        db.rollback()
        raise


def get_favorites_service(
    db: Session,
    user_id: int,
) -> list[FavoritePlace]:
    return (
        db.query(FavoritePlace)
        .options(joinedload(FavoritePlace.place))
        .filter(FavoritePlace.user_id == user_id)
        .order_by(FavoritePlace.id.asc())
        .all()
    )


def delete_favorite_service(
    db: Session,
    user_id: int,
    place_id: int,
) -> None:
    favorite = db.query(FavoritePlace).filter(
        FavoritePlace.user_id == user_id,
        FavoritePlace.place_id == place_id,
    ).first()

    if not favorite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Favorite not found",
        )

    try:
        db.delete(favorite)
        db.commit()

    except Exception:
        db.rollback()
        raise
