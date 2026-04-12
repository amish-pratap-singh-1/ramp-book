"""
Full seed script — inserts club, 5 aircraft, 3 instructors, 10 members, 1 admin,
15 reservations, and 1 maintenance window matching seed-data.json.
Run with: poetry run seed
"""

import asyncio
import datetime
import sys
from pathlib import Path

from src.entities.aircraft import Aircraft
from src.entities.club import Club
from src.entities.maintenance_window import MaintenanceWindow
from src.entities.reservation import Reservation, ReservationStatus
from src.entities.user import CertificateType, User, UserRole
from src.svc.dbsvc import DbSvc
from src.svc.secsvc import SecSvc

sys.path.append(str(Path(__file__).parent.parent))


sec = SecSvc()
db_svc = DbSvc()

DEFAULT_PASSWORD = "changeme123"


async def seed():
    async with db_svc.get_sessionmaker()() as db:

        # ── Club ──────────────────────────────────────────────────────────────
        club = Club(name="Cedar Valley Flying Club", home_base="KDTO")
        db.add(club)
        await db.flush()

        # ── Aircraft ──────────────────────────────────────────────────────────
        aircraft_data = [
            dict(
                tail_number="N7421T",
                model="Cessna 172S Skyhawk",
                year=2008,
                hourly_rate_usd=165.0,
                total_hobbs_hours=4821.3,
                notes="IFR equipped, G1000",
            ),
            dict(
                tail_number="N2198K",
                model="Cessna 172N Skyhawk",
                year=1978,
                hourly_rate_usd=135.0,
                total_hobbs_hours=9104.7,
                notes="Steam gauges, good primary trainer",
            ),
            dict(
                tail_number="N55XJ",
                model="Piper PA-28-161 Warrior III",
                year=2002,
                hourly_rate_usd=150.0,
                total_hobbs_hours=6310.0,
                notes="IFR equipped",
            ),
            dict(
                tail_number="N881SR",
                model="Cirrus SR20",
                year=2015,
                hourly_rate_usd=245.0,
                total_hobbs_hours=2190.5,
                notes="Checkout required",
            ),
            dict(
                tail_number="N304RG",
                model="Piper PA-28R-201 Arrow",
                year=1998,
                hourly_rate_usd=195.0,
                total_hobbs_hours=7855.2,
                notes="Complex aircraft, checkout required",
            ),
        ]
        aircraft_objs = []
        for ac in aircraft_data:
            obj = Aircraft(club_id=club.id, **ac)
            db.add(obj)
            aircraft_objs.append(obj)
        await db.flush()

        # ── Instructors ───────────────────────────────────────────────────────
        instructor_data = [
            dict(
                email="marcus.reilly@cedarvalleyfc.com",
                full_name="Marcus Reilly",
                ratings="CFI,CFII,MEI",
            ),
            dict(
                email="priya.natarajan@cedarvalleyfc.com",
                full_name="Priya Natarajan",
                ratings="CFI,CFII",
            ),
            dict(
                email="danielle.okafor@cedarvalleyfc.com",
                full_name="Danielle Okafor",
                ratings="CFI",
            ),
        ]
        instructor_objs = []
        for ins in instructor_data:
            obj = User(
                club_id=club.id,
                hashed_password=sec.hash_password(DEFAULT_PASSWORD),
                role=UserRole.INSTRUCTOR,
                is_active=True,
                **ins,
            )
            db.add(obj)
            instructor_objs.append(obj)
        await db.flush()

        # ── Members ───────────────────────────────────────────────────────────
        member_data = [
            dict(
                email="james.chen@cedarvalleyfc.com",
                full_name="James Chen",
                certificate=CertificateType.PRIVATE,
            ),
            dict(
                email="sofia.alvarez@cedarvalleyfc.com",
                full_name="Sofia Alvarez",
                certificate=CertificateType.PRIVATE,
            ),
            dict(
                email="henry.whitcombe@cedarvalleyfc.com",
                full_name="Henry Whitcombe",
                certificate=CertificateType.COMMERCIAL,
            ),
            dict(
                email="aisha.bello@cedarvalleyfc.com",
                full_name="Aisha Bello",
                certificate=CertificateType.STUDENT,
            ),
            dict(
                email="tomas.ribeiro@cedarvalleyfc.com",
                full_name="Tomas Ribeiro",
                certificate=CertificateType.PRIVATE,
            ),
            dict(
                email="ingrid.lindqvist@cedarvalleyfc.com",
                full_name="Ingrid Lindqvist",
                certificate=CertificateType.PRIVATE,
            ),
            dict(
                email="dev.malhotra@cedarvalleyfc.com",
                full_name="Dev Malhotra",
                certificate=CertificateType.STUDENT,
            ),
            dict(
                email="rachel.grossman@cedarvalleyfc.com",
                full_name="Rachel Grossman",
                certificate=CertificateType.ATP,
            ),
            dict(
                email="kofi.mensah@cedarvalleyfc.com",
                full_name="Kofi Mensah",
                certificate=CertificateType.PRIVATE,
            ),
            dict(
                email="eleanor.park@cedarvalleyfc.com",
                full_name="Eleanor Park",
                certificate=CertificateType.COMMERCIAL,
            ),
        ]
        member_objs = []
        for mem in member_data:
            obj = User(
                club_id=club.id,
                hashed_password=sec.hash_password(DEFAULT_PASSWORD),
                role=UserRole.MEMBER,
                is_active=True,
                **mem,
            )
            db.add(obj)
            member_objs.append(obj)

        # ── Admin ─────────────────────────────────────────────────────────────
        admin = User(
            club_id=club.id,
            email="walter.briggs@cedarvalleyfc.com",
            hashed_password=sec.hash_password(DEFAULT_PASSWORD),
            full_name="Walter Briggs",
            role=UserRole.ADMIN,
            is_active=True,
        )
        db.add(admin)
        await db.flush()

        # Index lookups (seed-data.json order → 0-based)
        ac = aircraft_objs  # ac[0]=N7421T, ac[1]=N2198K, ac[2]=N55XJ, ac[3]=N881SR, ac[4]=N304RG
        mb = member_objs  # mb[0]=James, mb[1]=Sofia, ... mb[9]=Eleanor
        ins = instructor_objs  # ins[0]=Marcus, ins[1]=Priya, ins[2]=Danielle

        # ── Reservations ──────────────────────────────────────────────────────
        def dt(s):
            return datetime.datetime.fromisoformat(s)

        reservations_data = [
            dict(
                aircraft=ac[0],
                member=mb[0],
                instructor=None,
                start=dt("2026-04-08T14:00:00-05:00"),
                end=dt("2026-04-08T16:30:00-05:00"),
            ),
            dict(
                aircraft=ac[1],
                member=mb[3],
                instructor=ins[1],
                start=dt("2026-04-08T15:00:00-05:00"),
                end=dt("2026-04-08T17:00:00-05:00"),
            ),
            dict(
                aircraft=ac[2],
                member=mb[1],
                instructor=None,
                start=dt("2026-04-09T08:00:00-05:00"),
                end=dt("2026-04-09T11:00:00-05:00"),
            ),
            dict(
                aircraft=ac[3],
                member=mb[7],
                instructor=None,
                start=dt("2026-04-09T13:00:00-05:00"),
                end=dt("2026-04-09T17:00:00-05:00"),
            ),
            dict(
                aircraft=ac[0],
                member=mb[4],
                instructor=None,
                start=dt("2026-04-10T09:00:00-05:00"),
                end=dt("2026-04-10T12:00:00-05:00"),
            ),
            dict(
                aircraft=ac[1],
                member=mb[6],
                instructor=ins[0],
                start=dt("2026-04-10T14:00:00-05:00"),
                end=dt("2026-04-10T16:00:00-05:00"),
            ),
            dict(
                aircraft=ac[4],
                member=mb[2],
                instructor=None,
                start=dt("2026-04-11T10:00:00-05:00"),
                end=dt("2026-04-11T13:30:00-05:00"),
            ),
            dict(
                aircraft=ac[2],
                member=mb[8],
                instructor=None,
                start=dt("2026-04-11T15:00:00-05:00"),
                end=dt("2026-04-11T18:00:00-05:00"),
            ),
            dict(
                aircraft=ac[0],
                member=mb[5],
                instructor=ins[2],
                start=dt("2026-04-12T09:00:00-05:00"),
                end=dt("2026-04-12T11:00:00-05:00"),
            ),
            dict(
                aircraft=ac[3],
                member=mb[9],
                instructor=None,
                start=dt("2026-04-12T13:00:00-05:00"),
                end=dt("2026-04-12T16:00:00-05:00"),
            ),
            dict(
                aircraft=ac[1],
                member=mb[0],
                instructor=None,
                start=dt("2026-04-13T08:00:00-05:00"),
                end=dt("2026-04-13T10:00:00-05:00"),
            ),
            dict(
                aircraft=ac[2],
                member=mb[3],
                instructor=ins[1],
                start=dt("2026-04-13T11:00:00-05:00"),
                end=dt("2026-04-13T13:00:00-05:00"),
            ),
            dict(
                aircraft=ac[4],
                member=mb[7],
                instructor=None,
                start=dt("2026-04-14T14:00:00-05:00"),
                end=dt("2026-04-14T17:00:00-05:00"),
            ),
            dict(
                aircraft=ac[0],
                member=mb[1],
                instructor=None,
                start=dt("2026-04-15T09:00:00-05:00"),
                end=dt("2026-04-15T12:00:00-05:00"),
            ),
            dict(
                aircraft=ac[1],
                member=mb[4],
                instructor=ins[0],
                start=dt("2026-04-15T15:00:00-05:00"),
                end=dt("2026-04-15T17:00:00-05:00"),
            ),
        ]
        for r in reservations_data:
            db.add(
                Reservation(
                    club_id=club.id,
                    aircraft_id=r["aircraft"].id,
                    member_id=r["member"].id,
                    instructor_id=(
                        r["instructor"].id if r["instructor"] else None
                    ),
                    start_time=r["start"],
                    end_time=r["end"],
                    status=ReservationStatus.CONFIRMED,
                )
            )

        # ── Maintenance window ─────────────────────────────────────────────
        db.add(
            MaintenanceWindow(
                club_id=club.id,
                aircraft_id=ac[3].id,  # N881SR Cirrus SR20
                start_time=dt("2026-04-16T00:00:00-05:00"),
                end_time=dt("2026-04-18T23:59:59-05:00"),
                reason="100-hour inspection",
            )
        )

        await db.commit()

        print("✓ Seeded successfully")
        print(f"  Club: {club.name} (id={club.id})")
        print(f"  Aircraft: {len(aircraft_objs)}")
        print(f"  Instructors: {len(instructor_objs)}")
        print(f"  Members: {len(member_objs)}")
        print(f"  Admin: {admin.email}")
        print(f"  Reservations: {len(reservations_data)}")
        print(f"\n  Password for all users: {DEFAULT_PASSWORD}")


def run():
    asyncio.run(seed())


if __name__ == "__main__":
    run()
