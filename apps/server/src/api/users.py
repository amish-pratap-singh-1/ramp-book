"""Users API router"""

from fastapi import APIRouter, Query, Request

from src.decorators.auth import protected
from src.entities.user import UserRole
from src.repositories.users import UserRepository
from src.schemas.user import UserListResponse, UserResponse, UserResponseWrapper
from src.svc.errsvc import UserNotFoundError

router = APIRouter(prefix="/users", tags=["Users"])

user_repo = UserRepository()


@router.get("/me", response_model=UserResponseWrapper)
@protected()
async def me(request: Request) -> UserResponseWrapper:
    """Get current authenticated user info"""
    user_id = int(request.state.user["sub"])
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise UserNotFoundError()
    return {"user": UserResponse.model_validate(user)}


@router.get("/instructors", response_model=UserListResponse)
@protected()
async def list_instructors(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
) -> UserListResponse:
    """List all active instructors in the club"""
    user_id = int(request.state.user["sub"])
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise UserNotFoundError()

    instructors, total = await user_repo.get_instructors(user.club_id, page, limit)

    return {
        "users": [UserResponse.model_validate(i) for i in instructors],
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total
        }
    }
