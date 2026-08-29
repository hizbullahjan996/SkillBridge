from typing import Any, Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class HealthResponse(BaseModel):
    status: str = "ok"
    service: str
    version: str


class DBHealthResponse(BaseModel):
    status: str
    database: str


class MessageResponse(BaseModel):
    message: str
    detail: Any = None


class ErrorResponse(BaseModel):
    detail: str


class PaginatedResponse(BaseModel, Generic[T]):
    data: list[T]
    total: int
    page: int
    page_size: int
    pages: int
