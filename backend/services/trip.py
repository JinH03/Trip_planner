
from datetime import timedelta

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.models import Trip, TripDay, User
from backend.schemas.trip import TripCreate, TripUpdate
from backend.services.place import resolve_destination_coordinates


def get_destination_coordinates_with_fallback(
    destination: str,
) -> tuple[float | None, float | None]:
    """
    목적지 좌표를 조회한다.

    Google API의 일시적 장애(502, 503, 504)라면
    좌표 없이 진행하고, 다른 오류는 다시 발생시킨다.
    """
    try:
        return resolve_destination_coordinates(destination)

    except HTTPException as exc:
        if exc.status_code not in (502, 503, 504):
            raise

        return None, None


def create_trip_with_days(
    db: Session,
    trip_data: TripCreate,
    current_user: User,
) -> Trip:
    if trip_data.end_date < trip_data.start_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End date must be on or after start date",
        )

    destination_latitude, destination_longitude = (
        get_destination_coordinates_with_fallback(
            trip_data.destination
        )
    )

    try:
        new_trip = Trip(
            user_id=current_user.id,
            title=trip_data.title,
            destination=trip_data.destination,
            destination_latitude=destination_latitude,
            destination_longitude=destination_longitude,
            start_date=trip_data.start_date,
            end_date=trip_data.end_date,
        )

        db.add(new_trip)

        # commit 전에 Trip ID 확보
        db.flush()

        total_days = (
            trip_data.end_date - trip_data.start_date
        ).days + 1

        for i in range(total_days):
            new_day = TripDay(
                trip_id=new_trip.id,
                day_number=i + 1,
                date=(
                    trip_data.start_date
                    + timedelta(days=i)
                ),
            )

            db.add(new_day)

        db.commit()
        db.refresh(new_trip)

        return new_trip

    except Exception:
        db.rollback()
        raise


def update_trip_with_days(
    db: Session,
    trip: Trip,
    trip_data: TripUpdate,
) -> Trip:
    if trip_data.end_date < trip_data.start_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End date must be on or after start date",
        )

    destination_changed = (
        trip.destination != trip_data.destination
    )

    if destination_changed:
        destination_latitude, destination_longitude = (
            get_destination_coordinates_with_fallback(
                trip_data.destination
            )
        )

    try:
        trip.title = trip_data.title
        trip.destination = trip_data.destination
        trip.start_date = trip_data.start_date
        trip.end_date = trip_data.end_date

        if destination_changed:
            trip.destination_latitude = destination_latitude
            trip.destination_longitude = destination_longitude

        total_days = (
            trip_data.end_date - trip_data.start_date
        ).days + 1

        existing_days = (
            db.query(TripDay)
            .filter(TripDay.trip_id == trip.id)
            .order_by(TripDay.day_number)
            .all()
        )

        # 기존 TripDay 날짜 갱신
        for i in range(
            min(len(existing_days), total_days)
        ):
            existing_days[i].day_number = i + 1
            existing_days[i].date = (
                trip_data.start_date
                + timedelta(days=i)
            )

        # 여행 기간 증가: TripDay 추가
        if total_days > len(existing_days):
            for i in range(
                len(existing_days),
                total_days,
            ):
                new_day = TripDay(
                    trip_id=trip.id,
                    day_number=i + 1,
                    date=(
                        trip_data.start_date
                        + timedelta(days=i)
                    ),
                )

                db.add(new_day)

        # 여행 기간 감소: 초과 TripDay 삭제
        elif total_days < len(existing_days):
            extra_days = existing_days[total_days:]

            for day in extra_days:
                db.delete(day)

        db.commit()
        db.refresh(trip)

        return trip

    except Exception:
        db.rollback()
        raise


def delete_trip_service(
    db: Session,
    trip: Trip,
) -> None:
    try:
        db.delete(trip)
        db.commit()

    except Exception:
        db.rollback()
        raise
