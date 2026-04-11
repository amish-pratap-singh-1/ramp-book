# entities/club.py
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.entities.base import Base


class Club(Base):
    __tablename__ = "clubs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    home_base: Mapped[str] = mapped_column(
        String(10), nullable=False)
    users: Mapped[list["User"]] = relationship(back_populates="club")
    aircraft: Mapped[list["Aircraft"]] = relationship(back_populates="club")
