from datetime import datetime, time

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, String, Time, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    email: Mapped[str | None] = mapped_column(
        String(255),
        unique=True,
        nullable=True,
        index=True
    )

    # 일반 이메일/비밀번호 로그인 사용자가 아니면 NULL 가능
    password_hash: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    # 이메일 인증 여부
    email_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    trips: Mapped[list["Trip"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )

    social_accounts: Mapped[list["SocialAccount"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    email_verifications: Mapped[list["EmailVerification"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )


class SocialAccount(Base):
    __tablename__ = "social_accounts"

    __table_args__ = (
        UniqueConstraint(
            "provider",
            "provider_user_id",
            name="uq_social_provider_user"
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    provider: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    provider_user_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    user: Mapped["User"] = relationship(
        back_populates="social_accounts"
    )

class Trip(Base):
    __tablename__ = "trips"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )

    destination: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )

    start_date: Mapped[datetime] = mapped_column(
        Date,
        nullable=False
    )

    end_date: Mapped[datetime] = mapped_column(
        Date,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    user: Mapped["User"] = relationship(
        back_populates="trips"
    )
    days: Mapped[list["TripDay"]] = relationship(
        back_populates="trip",
        cascade="all, delete-orphan",
    )
class TripDay(Base):
    __tablename__ = "trip_days"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    trip_id: Mapped[int] = mapped_column(
        ForeignKey("trips.id"),
        nullable=False,
        index=True,
    )

    day_number: Mapped[int] = mapped_column(
        nullable=False,
    )

    date: Mapped[datetime] = mapped_column(
        Date,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    trip: Mapped["Trip"] = relationship(
        back_populates="days",
    )
    schedules: Mapped[list["Schedule"]] = relationship(
        back_populates="trip_day",
        cascade="all, delete-orphan",
    )
class Schedule(Base):
    __tablename__ = "schedules"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    trip_day_id: Mapped[int] = mapped_column(
        ForeignKey("trip_days.id"),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    start_time: Mapped[time | None] = mapped_column(
        Time,
        nullable=True,
    )

    place: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
    )

    memo: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    order_index: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    trip_day: Mapped["TripDay"] = relationship(
        back_populates="schedules",
    )

class EmailVerification(Base):
    __tablename__ = "email_verifications"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    code_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False
    )

    verified_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    user: Mapped["User"] = relationship(
        back_populates="email_verifications"
    )