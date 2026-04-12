"""Aircraft service module"""

import logging

from src.entities.aircraft import Aircraft
from src.entities.maintenance_window import MaintenanceWindow
from src.repositories.aircraft import AircraftRepository
from src.repositories.maintenance import MaintenanceRepository
from src.schemas.aircraft import (AircraftCreate, AircraftScheduleItem,
                                  AircraftUpdate)
from src.schemas.maintenance import MaintenanceWindowCreate
from src.svc.errsvc import ResourceNotFoundError

logger = logging.getLogger(__name__)


class AircraftSvc:
    """Class for managing aircraft and maintenance logic"""

    def __init__(self):
        self.aircraft_repo = AircraftRepository()
        self.maint_repo = MaintenanceRepository()

    async def list_aircraft(
        self, club_id: int, page: int, limit: int
    ) -> tuple[list[Aircraft], int]:
        """List all aircraft in the club fleet"""
        return await self.aircraft_repo.get_all(club_id, page, limit)

    async def get_aircraft(self, aircraft_id: int) -> Aircraft:
        """Get a single aircraft by ID"""
        aircraft = await self.aircraft_repo.get_by_id(aircraft_id)
        if not aircraft:
            raise ResourceNotFoundError("Aircraft not found")
        return aircraft

    async def get_schedule(
        self, aircraft_id: int
    ) -> list[AircraftScheduleItem]:
        """Get non-identifying overlap schedule for an aircraft"""
        # First verify aircraft exists
        await self.get_aircraft(aircraft_id)
        return await self.aircraft_repo.get_schedule(aircraft_id)

    async def create_aircraft(
        self, club_id: int, data: AircraftCreate
    ) -> Aircraft:
        """Create a new aircraft (admin only)"""
        return await self.aircraft_repo.create(club_id, data)

    async def update_aircraft(
        self, aircraft_id: int, data: AircraftUpdate
    ) -> Aircraft:
        """Update aircraft details (admin only)"""
        aircraft = await self.aircraft_repo.update(aircraft_id, data)
        if not aircraft:
            raise ResourceNotFoundError("Aircraft not found")
        return aircraft

    async def list_maintenance(
        self, club_id: int, page: int, limit: int
    ) -> tuple[list[MaintenanceWindow], int]:
        """List all maintenance windows (admin only)"""
        return await self.maint_repo.get_all(club_id, page, limit)

    async def create_maintenance(
        self, club_id: int, data: MaintenanceWindowCreate
    ) -> MaintenanceWindow:
        """Create a maintenance window (admin only)"""
        return await self.maint_repo.create(club_id, data)

    async def delete_maintenance(self, window_id: int) -> None:
        """Delete a maintenance window (admin only)"""
        deleted = await self.maint_repo.delete(window_id)
        if not deleted:
            raise ResourceNotFoundError("Maintenance window not found")
