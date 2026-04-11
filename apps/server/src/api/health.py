"""App health router"""

from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check():
    """Api to check app health"""
    return {"status": "ok"}
