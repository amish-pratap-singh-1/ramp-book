"""User entity"""

import enum

from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.entities.base import Base, TimestampMixin


class UserRole(str, enum.Enum):
    """User role"""

    MEMBER = "member"
    INSTRUCTOR = "instructor"
    ADMIN = "admin"


class CertificateType(str, enum.Enum):
    """certificate type"""

    STUDENT = "Student"
    PRIVATE = "Private"
    COMMERCIAL = "Commercial"
    ATP = "ATP"


class User(TimestampMixin, Base):
    """User entity"""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    club_id: Mapped[int] = mapped_column(
        ForeignKey("clubs.id"), nullable=False, index=True
    )

    # Auth
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    # Identity
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(SAEnum(UserRole), nullable=False)

    # Member-specific (nullable for non-members)
    certificate: Mapped[CertificateType | None] = mapped_column(
        SAEnum(CertificateType), nullable=True
    )

    ratings: Mapped[str | None] = mapped_column(String(100), nullable=True)

    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    club: Mapped["Club"] = relationship(back_populates="users")
    reservations_as_member: Mapped[list["Reservation"]] = relationship(
        back_populates="member", foreign_keys="Reservation.member_id"
    )
    reservations_as_instructor: Mapped[list["Reservation"]] = relationship(
        back_populates="instructor", foreign_keys="Reservation.instructor_id"
    )
