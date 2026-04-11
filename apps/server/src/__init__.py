"""Root module init"""

from src.entities.aircraft import Aircraft
from src.entities.base import Base
from src.entities.club import Club
from src.entities.maintenance_window import MaintenanceWindow
from src.entities.reservation import Reservation
from src.entities.user import User

__all__ = [
    "Aircraft",
    "Base",
    "Club",
    "MaintenanceWindow",
    "Reservation",
    "User",
]

from src.svc.logsvc import LogSvc

# Initialize logger
LogSvc(__name__)
