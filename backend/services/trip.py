from datetime import timedelta

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.models import Trip, TripDay, User
from backend.schemas.trip import TripCreate, TripUpdate


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

    try:
        new_trip = Trip(
            user_id=current_user.id,
            title=trip_data.title,
            destination=trip_data.destination,
            start_date=trip_data.start_date,
            end_date=trip_data.end_date,
        )

        db.add(new_trip)

        # commit 전 new_trip.id 확보
        db.flush()

        total_days = (
            trip_data.end_date
            - trip_data.start_date
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

    try:
        trip.title = trip_data.title
        trip.destination = trip_data.destination
        trip.start_date = trip_data.start_date
        trip.end_date = trip_data.end_date

        total_days = (
            trip_data.end_date
            - trip_data.start_date
        ).days + 1

        existing_days = (
            db.query(TripDay)
            .filter(
                TripDay.trip_id == trip.id
            )
            .order_by(
                TripDay.day_number
            )
            .all()
        )

        # 기존 Day 날짜 갱신
        for i in range(
            min(len(existing_days), total_days)
        ):
            existing_days[i].day_number = i + 1
            existing_days[i].date = (
                trip_data.start_date
                + timedelta(days=i)
            )

        # 기간 증가 → Day 추가
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

        # 기간 감소 → 초과 Day 삭제
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