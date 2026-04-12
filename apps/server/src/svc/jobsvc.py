"""
Job Service Module using APScheduler
"""

import logging
from datetime import datetime, timedelta

from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import create_engine, select

from src.entities.aircraft import Aircraft
from src.schemas.maintenance import MaintenanceWindowCreate
from src.svc.dbsvc import DbSvc
from src.svc.secsvc import SecSvc

logger = logging.getLogger(__name__)


class JobSvc:
    """
    Singleton Job Service to manage background tasks
    """

    _instance = None
    _scheduler: AsyncIOScheduler = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(JobSvc, cls).__new__(cls)
            cls._instance._init_scheduler()
        return cls._instance

    def _init_scheduler(self) -> None:
        """Initialize the scheduler with a Postgres job store"""
        settings = SecSvc().get_appenv()

        jobstores = {
            "default": SQLAlchemyJobStore(url=settings.sync_database_url)
        }

        self._scheduler = AsyncIOScheduler(jobstores=jobstores)

    def start(self) -> None:
        """Start the scheduler if not already running"""
        if not self._scheduler.running:
            # Register recurring jobs here
            # Pass the static method instead of the instance method
            self._scheduler.add_job(
                JobSvc.check_aircraft_maintenance,
                "interval",
                minutes=60,
                id="check_maintenance",
                replace_existing=True,
                misfire_grace_time=300,
            )
            self._scheduler.start()
            logger.info("APScheduler started.")

    def shutdown(self) -> None:
        """Shutdown the scheduler"""
        if self._scheduler.running:
            self._scheduler.shutdown()
            logger.info("APScheduler shut down.")

    @staticmethod
    async def check_aircraft_maintenance() -> None:
        """
        Scan all aircraft and create maintenance windows if they reached 100hr hobbs
        """
        logger.info("Running automatic maintenance check...")
        db_svc = DbSvc()

        try:
            async with db_svc.get_sessionmaker()() as session:
                # Query all aircraft
                result = await session.execute(select(Aircraft))
                aircraft_list = result.scalars().all()

                for aircraft in aircraft_list:
                    # Check if 100 hours passed since last inspection
                    if (
                        aircraft.total_hobbs_hours
                        >= aircraft.last_100hr_inspection_hobbs + 100
                    ):
                        logger.info(
                            "Aircraft %s reached 100hr hobbs. Creating maintenance window.",
                            aircraft.tail_number,
                        )

                        # Create maintenance window starting now for 48 hours
                        start_time = datetime.now()
                        end_time = start_time + timedelta(hours=48)

                        # We use the AircraftSvc logic to handle reservation cancellations
                        from src.core.aircraftsvc import AircraftSvc

                        svc = AircraftSvc()
                        await svc.create_maintenance(
                            club_id=aircraft.club_id,
                            data=MaintenanceWindowCreate(
                                aircraft_id=aircraft.id,
                                start_time=start_time,
                                end_time=end_time,
                                reason="Automatic 100-Hour Inspection",
                            ),
                        )

                        # Update last inspection hobbs to the current major interval
                        new_last = (
                            int(aircraft.total_hobbs_hours / 100) * 100.0
                        )
                        aircraft.last_100hr_inspection_hobbs = new_last
                        session.add(aircraft)

                await session.commit()
                logger.info("Maintenance check completed.")

        except Exception as e:
            logger.error("Error in check_aircraft_maintenance job: %s", str(e))
