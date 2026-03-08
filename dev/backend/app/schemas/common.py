"""
Standard API response schemas with consistent format.
All responses include success, data/error, and meta (request_id + timestamp).
"""

from typing import Any, Dict, Generic, List, Optional, TypeVar
from pydantic import BaseModel
from datetime import datetime
import uuid

T = TypeVar("T")


class Meta(BaseModel):
    request_id: str = ""
    timestamp: str = ""

    def __init__(self, **data):
        if "request_id" not in data:
            data["request_id"] = f"req_{uuid.uuid4().hex[:8]}"
        if "timestamp" not in data:
            data["timestamp"] = datetime.utcnow().isoformat() + "Z"
        super().__init__(**data)


class APIResponse(BaseModel, Generic[T]):
    success: bool = True
    data: Optional[T] = None
    meta: Meta = Meta()


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    code: str
    meta: Meta = Meta()


class Pagination(BaseModel):
    page: int
    per_page: int
    total: int
    total_pages: int


class PaginatedResponse(BaseModel, Generic[T]):
    success: bool = True
    data: List[T]
    pagination: Pagination
    meta: Meta = Meta()


def ok(data: Any = None) -> dict:
    """Return a standardized success response with timestamp and request_id."""
    meta = Meta()
    return {"success": True, "data": data, "meta": meta.model_dump()}


def error(message: str, code: str = "INTERNAL_ERROR") -> dict:
    """Return a standardized error response with timestamp and request_id."""
    meta = Meta()
    return {
        "success": False,
        "error": message,
        "code": code,
        "meta": meta.model_dump(),
    }


def paginated(data: list, page: int, per_page: int, total: int) -> dict:
    """Return a standardized paginated response with timestamp and request_id."""
    meta = Meta()
    total_pages = max(1, (total + per_page - 1) // per_page)
    return {
        "success": True,
        "data": data,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": total_pages,
        },
        "meta": meta.model_dump(),
    }
