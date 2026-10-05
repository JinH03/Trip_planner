from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.dependencies.auth import get_current_user
from backend.models import Schedule, Trip, TripDay, User
from backend.schemas.schedule import (
    ScheduleCreate,
    ScheduleResponse,
    ScheduleUpdate,
    ScheduleReorderRequest,
)


router = APIRouter(
    prefix="/trip-days/{trip_day_id}/schedules",
    tags=["schedules"],
)


@router.post(
    "",
    response_model=ScheduleResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_schedule(
    trip_day_id: int,
    schedule: ScheduleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    trip_day = (
        db.query(TripDay)
        .join(Trip)
        .filter(
            TripDay.id == trip_day_id,
            Trip.user_id == current_user.id,
        )
        .first()
    )

    if not trip_day:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip day not found",
        )

    new_schedule = Schedule(
        trip_day_id=trip_day.id,
        title=schedule.title,
        start_time=schedule.start_time,
        place=schedule.place,
        memo=schedule.memo,
        order_index=schedule.order_index,
    )

    db.add(new_schedule)
    db.commit()
    db.refresh(new_schedule)

    return new_schedule


@router.get(
    "",
    response_model=list[ScheduleResponse],
)
def get_schedules(
    trip_day_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    trip_day = (
        db.query(TripDay)
        .join(Trip)
        .filter(
            TripDay.id == trip_day_id,
            Trip.user_id == current_user.id,
        )
        .first()
    )

    if not trip_day:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip day not found",
        )

    schedules = (
        db.query(Schedule)
        .filter(Schedule.trip_day_id == trip_day.id)
        .order_by(Schedule.order_index)
        .all()
    )

    return schedules

@router.get(
    "/{schedule_id}",
    response_model=ScheduleResponse,
)
def get_schedule(
    trip_day_id: int,
    schedule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    schedule = (
        db.query(Schedule)
        .join(TripDay)
        .join(Trip)
        .filter(
            Schedule.id == schedule_id,
            Schedule.trip_day_id == trip_day_id,
            Trip.user_id == current_user.id,
        )
        .first()
    )

    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found",
        )

    return schedule

@router.put(
    "/reorder",
    response_model=list[ScheduleResponse],
)
def reorder_schedules(
    trip_day_id: int,
    request: ScheduleReorderRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    trip_day = (
        db.query(TripDay)
        .join(Trip)
        .filter(
            TripDay.id == trip_day_id,
            Trip.user_id == current_user.id,
        )
        .first()
    )

    if not trip_day:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip day not found",
        )

    schedule_ids = [
        item.schedule_id
        for item in request.schedules
    ]

    schedules = (
        db.query(Schedule)
        .filter(
            Schedule.trip_day_id == trip_day.id,
            Schedule.id.in_(schedule_ids),
        )
        .all()
    )

    if len(schedules) != len(schedule_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="One or more schedules are invalid",
        )

    schedule_map = {
        schedule.id: schedule
        for schedule in schedules
    }

    for item in request.schedules:
        schedule = schedule_map[item.schedule_id]
        schedule.order_index = item.order_index

    db.commit()

    updated_schedules = (
        db.query(Schedule)
        .filter(
            Schedule.trip_day_id == trip_day.id
        )
        .order_by(Schedule.order_index)
        .all()
    )

    return updated_schedules

@router.put(
    "/{schedule_id}",
    response_model=ScheduleResponse,
)

def update_schedule(
    trip_day_id: int,
    schedule_id: int,
    schedule_update: ScheduleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    schedule = (
        db.query(Schedule)
        .join(TripDay)
        .join(Trip)
        .filter(
            Schedule.id == schedule_id,
            Schedule.trip_day_id == trip_day_id,
            Trip.user_id == current_user.id,
        )
        .first()
    )

    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found",
        )

    schedule.title = schedule_update.title
    schedule.start_time = schedule_update.start_time
    schedule.place = schedule_update.place
    schedule.memo = schedule_update.memo
    schedule.order_index = schedule_update.order_index

    db.commit()
    db.refresh(schedule)

    return schedule

@router.delete(
    "/{schedule_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_schedule(
    trip_day_id: int,
    schedule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    schedule = (
        db.query(Schedule)
        .join(TripDay)
        .join(Trip)
        .filter(
            Schedule.id == schedule_id,
            Schedule.trip_day_id == trip_day_id,
            Trip.user_id == current_user.id,
        )
        .first()
    )

    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found",
        )

    db.delete(schedule)
    db.commit()
