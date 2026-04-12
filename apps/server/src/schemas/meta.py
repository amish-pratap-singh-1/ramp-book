"""Common metadata schemas"""

from pydantic import BaseModel


class Pagination(BaseModel):
    """Pagination metadata"""
    page: int
    limit: int
    total: int
