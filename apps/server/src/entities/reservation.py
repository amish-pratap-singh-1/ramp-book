# entities/reservation.py
import datetime
import enum

from sqlalchemy import CheckConstraint, DateTime
from sqlalchemy import Enum as SAEnum
from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.entities.base import Base, TimestampMixin


class ReservationStatus(str, enum.Enum):
    confirmed = "confirmed"
    cancelled = "cancelled"
    completed = "completed"  # flight happened, Hobbs logged


class Reservation(TimestampMixin, Base):
    __tablename__ = "reservations"

    __table_args__ = (
        # DB-level guard: end must be after start
        CheckConstraint(
            "end_time > start_time", name="ck_reservation_end_after_start"
        ),
        CheckConstraint(
            "hobbs_end > hobbs_start", name="ck_hobbs_end_after_start"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    club_id: Mapped[int] = mapped_column(
        ForeignKey("clubs.id"), nullable=False, index=True
    )

    aircraft_id: Mapped[int] = mapped_column(
        ForeignKey("aircraft.id"), nullable=False, index=True
    )
    member_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    instructor_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True, index=True
    )

    # Always store as UTC in the DB — display in club's local timezone on the frontend
    start_time: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    end_time: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    status: Mapped[ReservationStatus] = mapped_column(
        SAEnum(ReservationStatus),
        nullable=False,
        default=ReservationStatus.confirmed,
    )

    # Filled in when member completes the flight
    hobbs_start: Mapped[float | None] = mapped_column(Float, nullable=True)
    hobbs_end: Mapped[float | None] = mapped_column(Float, nullable=True)

    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Relationships
    aircraft: Mapped["Aircraft"] = relationship(back_populates="reservations")
    member: Mapped["User"] = relationship(
        back_populates="reservations_as_member", foreign_keys=[member_id]
    )
    instructor: Mapped["User | None"] = relationship(
        back_populates="reservations_as_instructor",
        foreign_keys=[instructor_id],
    )
