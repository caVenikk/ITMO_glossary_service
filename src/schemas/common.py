from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page_size: int


def paginate(items: list[T], total: int, page_size: int) -> PaginatedResponse[T]:
    return PaginatedResponse(items=items, total=total, page_size=page_size)
