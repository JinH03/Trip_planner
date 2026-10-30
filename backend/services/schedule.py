
from datetime import time

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.models import Place, Schedule, TripDay
from backend.schemas.schedule import (
    ScheduleCreate,
    ScheduleReorderRequest,
    ScheduleUpdate,
)
from typing import Literal
from sqlalchemy import nulls_last


def get_schedules_sorted_service(
    db: Session,
    trip_day_id: int,
    sort_by: Literal["manual", "time"] = "manual",
) -> list[Schedule]:

    query = db.query(Schedule).filter(
        Schedule.trip_day_id == trip_day_id
    )

    if sort_by == "time":
        query = query.order_by(
            nulls_last(Schedule.start_time.asc()),
            Schedule.order_index.asc(),
            Schedule.id.asc(),
        )

    else:
        query = query.order_by(
            Schedule.order_index.asc(),
            Schedule.id.asc(),
        )

    return query.all()

def validate_schedule_conflict(
    db: Session,
    trip_day_id: int,
    start_time: time | None,
    end_time: time | None,
    exclude_schedule_id: int | None = None,
) -> None:
    """
    같은 TripDay에서 시간이 겹치는 Schedule이 있는지 확인한다.

    종료 시간이 없는 일정은 충돌 검사에서 제외한다.
    수정 중인 일정은 자기 자신과 비교하지 않는다.
    """

    if start_time is None or end_time is None:
        return

    query = db.query(Schedule).filter(
        Schedule.trip_day_id == trip_day_id,
        Schedule.start_time.isnot(None),
        Schedule.end_time.isnot(None),
        Schedule.start_time < end_time,
        Schedule.end_time > start_time,
    )

    if exclude_schedule_id is not None:
        query = query.filter(
            Schedule.id != exclude_schedule_id
        )

    existing_schedule = query.first()

    if existing_schedule:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Schedule time conflicts with an existing schedule",
        )


def validate_place_id(
    db: Session,
    place_id: int | None,
) -> None:
    """
    등록하려는 Place가 실제로 존재하는지 확인한다.
    """

    if place_id is None:
        return

    place = (
        db.query(Place)
        .filter(Place.id == place_id)
        .first()
    )

    if not place:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid place_id",
        )


def create_schedule_service(
    db: Session,
    trip_day: TripDay,
    schedule_data: ScheduleCreate,
) -> Schedule:
    validate_place_id(
        db=db,
        place_id=schedule_data.place_id,
    )

    validate_schedule_conflict(
        db=db,
        trip_day_id=trip_day.id,
        start_time=schedule_data.start_time,
        end_time=schedule_data.end_time,
    )

    new_schedule = Schedule(
        trip_day_id=trip_day.id,
        title=schedule_data.title,
        start_time=schedule_data.start_time,
        end_time=schedule_data.end_time,
        place=schedule_data.place,
        place_id=schedule_data.place_id,
        memo=schedule_data.memo,
        order_index=schedule_data.order_index,
    )

    try:
        db.add(new_schedule)
        db.commit()
        db.refresh(new_schedule)

        return new_schedule

    except Exception:
        db.rollback()
        raise


def update_schedule_service(
    db: Session,
    schedule: Schedule,
    schedule_data: ScheduleUpdate,
) -> Schedule:
    validate_place_id(
        db=db,
        place_id=schedule_data.place_id,
    )

    validate_schedule_conflict(
        db=db,
        trip_day_id=schedule.trip_day_id,
        start_time=schedule_data.start_time,
        end_time=schedule_data.end_time,
        exclude_schedule_id=schedule.id,
    )

    try:
        schedule.title = schedule_data.title
        schedule.start_time = schedule_data.start_time
        schedule.end_time = schedule_data.end_time
        schedule.place = schedule_data.place
        schedule.place_id = schedule_data.place_id
        schedule.memo = schedule_data.memo
        schedule.order_index = schedule_data.order_index

        db.commit()
        db.refresh(schedule)

        return schedule

    except Exception:
        db.rollback()
        raise


def delete_schedule_service(
    db: Session,
    schedule: Schedule,
) -> None:
    try:
        db.delete(schedule)
        db.commit()

    except Exception:
        db.rollback()
        raise


def reorder_schedules_service(
    db: Session,
    trip_day: TripDay,
    request: ScheduleReorderRequest,
) -> list[Schedule]:
    schedule_ids = [
        item.schedule_id
        for item in request.schedules
    ]

    if len(schedule_ids) != len(set(schedule_ids)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Duplicate schedule_id is not allowed",
        )

    order_indexes = [
        item.order_index
        for item in request.schedules
    ]

    if len(order_indexes) != len(set(order_indexes)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Duplicate order_index is not allowed",
        )

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

    try:
        for item in request.schedules:
            schedule = schedule_map[item.schedule_id]
            schedule.order_index = item.order_index

        db.commit()

        updated_schedules = (
            db.query(Schedule)
            .filter(
                Schedule.trip_day_id == trip_day.id
            )
            .order_by(
                Schedule.order_index,
                Schedule.start_time,
            )
            .all()
        )

        return updated_schedules

    except Exception:
        db.rollback()
        raise
