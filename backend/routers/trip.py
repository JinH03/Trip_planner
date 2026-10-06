from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
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
    if trip.end_date < trip.start_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End date must be on or after start date",
        )
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
    total_days = (new_trip.end_date - new_trip.start_date).days+1
    for i in range(total_days):
        trip_day = TripDay(
            trip_id=new_trip.id,
            day_number=i + 1,
            date=new_trip.start_date + timedelta(days=i),
        )
        db.add(trip_day)
    db.commit()
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
            key=lambda schedule: (
                schedule.order_index,
                schedule.start_time is None,
                schedule.start_time,
            )
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
    if trip_update.end_date < trip_update.start_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End date must be on or after start date",
        )
    trip.title = trip_update.title
    trip.destination = trip_update.destination
    trip.start_date = trip_update.start_date
    trip.end_date = trip_update.end_date
    total_days = (trip_update.end_date - trip_update.start_date).days + 1
    existing_days = (db.query(TripDay).filter(TripDay.trip_id == trip.id).order_by(TripDay.day_number).all())
    for i in range(min(len(existing_days), total_days)):
        existing_days[i].day_number = i + 1
        existing_days[i].date = trip_update.start_date + timedelta(days=i)
    if total_days > len(existing_days):
        for i in range(len(existing_days), total_days):
            new_day = TripDay(
                trip_id = trip.id,
                day_number = i + 1,
                date = trip_update.start_date + timedelta(days=i),
            )
            db.add(new_day)
    elif total_days < len(existing_days):
        extra_days = existing_days[total_days:]
        for day in extra_days:
            db.delete(day)

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