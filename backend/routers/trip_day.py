from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.dependencies.auth import get_current_user
from backend.models import Trip, TripDay, User
from backend.schemas.trip_day import (
    TripDayCreate,
    TripDayResponse,
    TripDayUpdate,
)


router = APIRouter(
    prefix="/trips/{trip_id}/days",
    tags=["trip-days"],
)


@router.post(
    "",
    response_model=TripDayResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_trip_day(
    trip_id: int,
    trip_day: TripDayCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    trip = (
        db.query(Trip)
        .filter(
            Trip.id == trip_id,
            Trip.user_id == current_user.id,
        )
        .first()
    )

    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found",
        )
    if not (
        trip.start_date <= trip_day.date <= trip.end_date
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Trip day date must be within trip dates",
        )

    existing_day = (
        db.query(TripDay)
        .filter(
            TripDay.trip_id == trip.id,
            TripDay.day_number == trip_day.day_number,
        )
        .first()
    )

    if existing_day:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Day number already exists",
        )
    new_day = TripDay(
        trip_id=trip.id,
        day_number=trip_day.day_number,
        date=trip_day.date,
    )

    db.add(new_day)
    db.commit()
    db.refresh(new_day)

    return new_day


@router.get(
    "",
    response_model=list[TripDayResponse],
)
def get_trip_days(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    trip = (
        db.query(Trip)
        .filter(
            Trip.id == trip_id,
            Trip.user_id == current_user.id,
        )
        .first()
    )

    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found",
        )

    days = (
        db.query(TripDay)
        .filter(TripDay.trip_id == trip.id)
        .order_by(TripDay.day_number)
        .all()
    )

    return days

@router.put(
    "/{trip_day_id}",
    response_model=TripDayResponse,
)
def update_trip_day(
    trip_id: int,
    trip_day_id: int,
    trip_day_update: TripDayUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    trip = (
        db.query(Trip)
        .filter(
            Trip.id == trip_id,
            Trip.user_id == current_user.id,
        )
        .first()
    )

    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found",
        )

    trip_day = (
        db.query(TripDay)
        .filter(
            TripDay.id == trip_day_id,
            TripDay.trip_id == trip.id,
        )
        .first()
    )

    if not trip_day:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip day not found",
        )

    if not (
        trip.start_date <= trip_day_update.date <= trip.end_date
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Trip day date must be within trip dates",
        )

    duplicate_day = (
        db.query(TripDay)
        .filter(
            TripDay.trip_id == trip.id,
            TripDay.day_number == trip_day_update.day_number,
            TripDay.id != trip_day.id,
        )
        .first()
    )

    if duplicate_day:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Day number already exists",
        )

    trip_day.day_number = trip_day_update.day_number
    trip_day.date = trip_day_update.date

    db.commit()
    db.refresh(trip_day)

    return trip_day


@router.delete(
    "/{trip_day_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_trip_day(
    trip_id: int,
    trip_day_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    trip = (
        db.query(Trip)
        .filter(
            Trip.id == trip_id,
            Trip.user_id == current_user.id,
        )
        .first()
    )

    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found",
        )

    trip_day = (
        db.query(TripDay)
        .filter(
            TripDay.id == trip_day_id,
            TripDay.trip_id == trip.id,
        )
        .first()
    )

    if not trip_day:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip day not found",
        )

    db.delete(trip_day)
    db.commit()