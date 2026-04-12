"""Fastapi app"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.admin import router as admin_router
from src.api.aircraft import router as aircraft_router
from src.api.auth import router as auth_router
from src.api.health import router as health_router
from src.api.reservations import router as reservations_router
from src.api.users import router as users_router
from src.svc.errsvc import AppError, ErrSvc
from src.svc.jobsvc import JobSvc


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Lifecycle events for the FastAPI application"""
    # Startup
    JobSvc().start()
    yield
    # Shutdown
    JobSvc().shutdown()


app = FastAPI(redoc_url=None, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js
    ],
    allow_credentials=True,
    allow_methods=["*"],  # IMPORTANT (includes OPTIONS)
    allow_headers=["*"],
)

# Global error handling
app.add_exception_handler(AppError, ErrSvc.app_error_handler)

app.include_router(health_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(aircraft_router, prefix="/api/v1")
app.include_router(reservations_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/v1")
