"""
Quick seed script — inserts one club, one member, one instructor, one admin.
Run with: poetry run seed
"""

import asyncio
import sys
from pathlib import Path

from src.entities.club import Club
from src.entities.user import CertificateType, User, UserRole
from src.svc.dbsvc import DbSvc
from src.svc.secsvc import SecSvc

sys.path.append(str(Path(__file__).parent.parent))


sec = SecSvc()
db_svc = DbSvc()


async def seed():
    async with db_svc.get_sessionmaker()() as db:
        # --- Club (required for FK) ---
        club = Club(
            name="Cedar Valley Flying Club",
            home_base="KDTO",
        )
        db.add(club)
        await db.flush()  # get club.id before inserting users

        # --- Member ---
        member = User(
            club_id=club.id,
            email="james.chen@cedarvalleyfc.com",
            hashed_password=sec.hash_password("changeme123"),
            full_name="James Chen",
            role=UserRole.MEMBER,
            certificate=CertificateType.PRIVATE,
            is_active=True,
        )

        # --- Instructor ---
        instructor = User(
            club_id=club.id,
            email="marcus.reilly@cedarvalleyfc.com",
            hashed_password=sec.hash_password("changeme123"),
            full_name="Marcus Reilly",
            role=UserRole.INSTRUCTOR,
            ratings="CFI,CFII,MEI",
            is_active=True,
        )

        # --- Admin ---
        admin = User(
            club_id=club.id,
            email="walter.briggs@cedarvalleyfc.com",
            hashed_password=sec.hash_password("changeme123"),
            full_name="Walter Briggs",
            role=UserRole.ADMIN,
            is_active=True,
        )

        db.add_all([member, instructor, admin])
        await db.commit()

        print("✓ Seeded successfully")
        print(f"  Club:       {club.name} (id={club.id})")
        print(f"  Member:     {member.email}")
        print(f"  Instructor: {instructor.email}")
        print(f"  Admin:      {admin.email}")
        print(f"\n  Password for all users: changeme123")


def run():
    asyncio.run(seed())


if __name__ == "__main__":
    run()
