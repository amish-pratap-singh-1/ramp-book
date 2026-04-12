"""App health router"""

from fastapi import APIRouter

from src.schemas.health import HealthResponse
from src.svc.errsvc import ErrSvc

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        return {"health": {"status": "ok", "message": "server is healthy"}}
    except Exception as e:
        raise ErrSvc.handle_api_error(e)
