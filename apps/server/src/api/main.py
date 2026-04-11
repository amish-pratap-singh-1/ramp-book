"""Fastapi app"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.auth import router as auth_router
from src.api.health import router as health_router
from src.svc.errsvc import AppError, ErrSvc

app = FastAPI(redoc_url=None)

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
