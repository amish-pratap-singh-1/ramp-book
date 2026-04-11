from sqlalchemy.orm import DeclarativeBase
# type: ignore[attr-defined]  # noqa
from sqlalchemy import DateTime, text
from sqlalchemy.orm import Mapped, mapped_column
import datetime


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("TIMEZONE('utc', now())"),
        nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("TIMEZONE('utc', now())"),
        onupdate=lambda: datetime.datetime.now(datetime.timezone.utc),
        nullable=False
    )
