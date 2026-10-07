from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.models import Schedule, TripDay
from backend.schemas.schedule import (
    ScheduleCreate,
    ScheduleReorderRequest,
    ScheduleUpdate,
)


def create_schedule_service(
    db: Session,
    trip_day: TripDay,
    schedule_data: ScheduleCreate,
) -> Schedule:
    new_schedule = Schedule(
        trip_day_id=trip_day.id,
        title=schedule_data.title,
        start_time=schedule_data.start_time,
        place=schedule_data.place,
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
    try:
        schedule.title = schedule_data.title
        schedule.start_time = schedule_data.start_time
        schedule.place = schedule_data.place
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