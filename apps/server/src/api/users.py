"""Users API router"""

from fastapi import APIRouter, Query, Request

from src.core.usrsvc import UsrSvc
from src.decorators.auth import protected
from src.schemas.user import (UserListResponse, UserResponse,
                              UserResponseWrapper)

router = APIRouter(prefix="/users", tags=["Users"])

usr_svc = UsrSvc()


@router.get("/me", response_model=UserResponseWrapper)
@protected()
async def me(request: Request) -> UserResponseWrapper:
    """Get current authenticated user info"""
    user_id = int(request.state.user["sub"])
    user = await usr_svc.get_me(user_id)
    return {"user": UserResponse.model_validate(user)}


@router.get("/instructors", response_model=UserListResponse)
@protected()
async def list_instructors(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
) -> UserListResponse:
    """List all active instructors in the club"""
    user_id = int(request.state.user["sub"])

    instructors, total = await usr_svc.list_instructors(user_id, page, limit)

    return {
        "users": [UserResponse.model_validate(i) for i in instructors],
        "pagination": {"page": page, "limit": limit, "total": total},
    }
