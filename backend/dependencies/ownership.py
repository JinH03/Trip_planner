from fastapi import HTTPException, Depends, status
from sqlalchemy.orm import Session
from backend.models import Schedule, Trip, User, TripDay
from backend.routers import user

def get_owned_trip(
    db: Session,
    trip_id: int,
    user_id: int,
) -> Trip:
    trip = (
        db.query(Trip)
        .filter(trip_id == Trip.id, Trip.user_id == user_id)
        .first()
    )
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found",
        )
    return trip
def get_owned_trip_day(
    db: Session,
    trip_day_id: int,
    user_id: int,
) -> TripDay:
    trip_day = (
        db.query(TripDay)
        .join(Trip)
        .filter(
            trip_day_id == TripDay.id,
            Trip.user_id == user_id,
        )
        .first()
    )
    if not trip_day:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip day not found",
        )
    return trip_day


def get_owned_schedule(
    db: Session,
    trip_day_id: int,
    schedule_id: int,
    user_id: int,
) -> Schedule:
    schedule = (
        db.query(Schedule)
        .join(TripDay)
        .join(Trip)
        .filter(
            Schedule.id == schedule_id,
            Schedule.trip_day_id == trip_day_id,
            Trip.user_id == user_id,
        )
        .first()
    )

    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found",
        )

    return schedule