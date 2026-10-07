from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from backend.database import get_db
from backend.dependencies.auth import get_current_user
from backend.dependencies.ownership import get_owned_trip
from backend.models import Trip, TripDay, User
from backend.schemas.trip import (
    TripCreate,
    TripDetailResponse,
    TripResponse,
    TripUpdate,
)
from backend.services.trip import (
    create_trip_with_days,
    delete_trip_service,
    update_trip_with_days,
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
    return create_trip_with_days(
        db=db,
        trip_data=trip,
        current_user=current_user,
    )


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
        .filter(
            Trip.user_id == current_user.id
        )
        .all()
    )

    return trips


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
            joinedload(Trip.days)
            .joinedload(TripDay.schedules)
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


@router.get(
    "/{trip_id}",
    response_model=TripResponse,
)
def get_trip(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_owned_trip(
        db=db,
        trip_id=trip_id,
        user_id=current_user.id,
    )


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
    trip = get_owned_trip(
        db=db,
        trip_id=trip_id,
        user_id=current_user.id,
    )

    return update_trip_with_days(
        db=db,
        trip=trip,
        trip_data=trip_update,
    )


@router.delete(
    "/{trip_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_trip(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    trip = get_owned_trip(
        db=db,
        trip_id=trip_id,
        user_id=current_user.id,
    )

    delete_trip_service(
        db=db,
        trip=trip,
    )