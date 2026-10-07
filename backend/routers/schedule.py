from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.dependencies.auth import get_current_user
from backend.dependencies.ownership import (
    get_owned_schedule,
    get_owned_trip_day,
)
from backend.models import Schedule, User
from backend.schemas.schedule import (
    ScheduleCreate,
    ScheduleReorderRequest,
    ScheduleResponse,
    ScheduleUpdate,
)
from backend.services.schedule import (
    create_schedule_service,
    delete_schedule_service,
    reorder_schedules_service,
    update_schedule_service,
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
    trip_day = get_owned_trip_day(
        db=db,
        trip_day_id=trip_day_id,
        user_id=current_user.id,
    )

    return create_schedule_service(
        db=db,
        trip_day=trip_day,
        schedule_data=schedule,
    )


@router.get(
    "",
    response_model=list[ScheduleResponse],
)
def get_schedules(
    trip_day_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    trip_day = get_owned_trip_day(
        db=db,
        trip_day_id=trip_day_id,
        user_id=current_user.id,
    )

    schedules = (
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

    return schedules


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
    trip_day = get_owned_trip_day(
        db=db,
        trip_day_id=trip_day_id,
        user_id=current_user.id,
    )

    return reorder_schedules_service(
        db=db,
        trip_day=trip_day,
        request=request,
    )


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
    return get_owned_schedule(
        db=db,
        trip_day_id=trip_day_id,
        schedule_id=schedule_id,
        user_id=current_user.id,
    )


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
    schedule = get_owned_schedule(
        db=db,
        trip_day_id=trip_day_id,
        schedule_id=schedule_id,
        user_id=current_user.id,
    )

    return update_schedule_service(
        db=db,
        schedule=schedule,
        schedule_data=schedule_update,
    )


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
    schedule = get_owned_schedule(
        db=db,
        trip_day_id=trip_day_id,
        schedule_id=schedule_id,
        user_id=current_user.id,
    )

    delete_schedule_service(
        db=db,
        schedule=schedule,
    )