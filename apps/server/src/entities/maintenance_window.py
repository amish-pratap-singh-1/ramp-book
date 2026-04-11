# entities/maintenance_window.py
import datetime

from sqlalchemy import DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.entities.base import Base, TimestampMixin


class MaintenanceWindow(TimestampMixin, Base):
    __tablename__ = "maintenance_windows"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    club_id: Mapped[int] = mapped_column(
        ForeignKey("clubs.id"), nullable=False, index=True
    )
    aircraft_id: Mapped[int] = mapped_column(
        ForeignKey("aircraft.id"), nullable=False, index=True
    )

    start_time: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    end_time: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    aircraft: Mapped["Aircraft"] = relationship(
        back_populates="maintenance_windows"
    )
