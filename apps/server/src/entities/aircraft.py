"""Aircraft Entity"""

import enum

from sqlalchemy import Enum as SAEnum
from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.entities.base import Base, TimestampMixin


class AircraftStatus(str, enum.Enum):
    """Status enum"""

    AVAILABLE = "available"
    MAINTENANCE = "maintenance"
    RETIRED = "retired"


class Aircraft(TimestampMixin, Base):
    """Aircraft entity"""

    __tablename__ = "aircraft"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    club_id: Mapped[int] = mapped_column(
        ForeignKey("clubs.id"), nullable=False, index=True
    )

    tail_number: Mapped[str] = mapped_column(
        String(10), unique=True, nullable=False, index=True
    )
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    hourly_rate_usd: Mapped[float] = mapped_column(Float, nullable=False)

    total_hobbs_hours: Mapped[float] = mapped_column(
        Float, nullable=False, default=0.0
    )
    last_100hr_inspection_hobbs: Mapped[float] = mapped_column(
        Float, nullable=False, default=0.0
    )

    status: Mapped[AircraftStatus] = mapped_column(
        SAEnum(AircraftStatus),
        nullable=False,
        default=AircraftStatus.AVAILABLE,
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    club: Mapped["Club"] = relationship(back_populates="aircraft")
    reservations: Mapped[list["Reservation"]] = relationship(
        back_populates="aircraft"
    )
    maintenance_windows: Mapped[list["MaintenanceWindow"]] = relationship(
        back_populates="aircraft"
    )
