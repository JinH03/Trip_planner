from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.dependencies.auth import get_current_user
from backend.models import Trip, User, TripDay
from backend.schemas.trip import TripCreate, TripResponse, TripUpdate
from sqlalchemy.orm import joinedload
from backend.schemas.trip import (
    TripCreate,
    TripUpdate,
    TripResponse,
    TripDetailResponse,
)
router = APIRouter(
    prefix="/trips",
    tags=["trips"],
)


@router.post(
    "",
    response_model=TripResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_trip(
    trip: TripCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    new_trip = Trip(
        user_id=current_user.id,
        title=trip.title,
        destination=trip.destination,
        start_date=trip.start_date,
        end_date=trip.end_date,
    )

    db.add(new_trip)
    db.commit()
    db.refresh(new_trip)

    return new_trip


@router.get(
    "",
    response_model=list[TripResponse],
)
def get_my_trips(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    trips = (
        db.query(Trip)
        .filter(Trip.user_id == current_user.id)
        .all()
    )

    return trips

@router.get(
    "/{trip_id}",
    response_model=TripResponse,
)
def get_trip(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    trip = (
        db.query(Trip)
        .filter(Trip.id == trip_id, Trip.user_id == current_user.id)
        .first()
    )

    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found",
        )

    return trip
@router.get(
    "/{trip_id}/detail",
    response_model=TripDetailResponse,
)
def get_trip_detail(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    trip = (
        db.query(Trip)
        .options(
            joinedload(Trip.days).joinedload(TripDay.schedules)
        )
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

    trip.days.sort(
        key=lambda day: day.day_number
    )

    for day in trip.days:
        day.schedules.sort(
            key=lambda schedule: schedule.order_index
        )

    return trip
@router.put(
    "/{trip_id}",
    response_model=TripResponse,
)
def update_trip(
    trip_id: int,
    trip_update: TripUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    trip = (
        db.query(Trip)
        .filter(Trip.id == trip_id, Trip.user_id == current_user.id)
        .first()
    )

    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found",
        )

    trip.title = trip_update.title
    trip.destination = trip_update.destination
    trip.start_date = trip_update.start_date
    trip.end_date = trip_update.end_date

    db.commit()
    db.refresh(trip)

    return trip

@router.delete(
    "/{trip_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_trip(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    trip = (
        db.query(Trip)
        .filter(Trip.id == trip_id, Trip.user_id == current_user.id)
        .first()
    )

    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found",
        )

    db.delete(trip)
    db.commit()

    return None