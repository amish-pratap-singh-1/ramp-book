"""Fastapi app"""

from fastapi import FastAPI

from src.api.auth import router as auth_router
from src.api.health import router as health_router
from src.svc.errsvc import AppError, ErrSvc

app = FastAPI(redoc_url=None)

# Global error handling
app.add_exception_handler(AppError, ErrSvc.app_error_handler)

app.include_router(health_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
