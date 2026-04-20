from typing import Any, Dict, Generic, Optional, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")
M = TypeVar("M", default=None)


class PaginationParams(BaseModel):
    """Pagination parameters for endpoints"""

    Page: int = Field(default=1, ge=1, description="Page number (minimum 1)")
    Page_size: int = Field(default=10, ge=1, le=100, description="Page size (1-100)")


class PaginationMetadata(BaseModel):
    """Pagination metadata for responses"""

    Page: int
    Limit: int
    Total_items: int
    Total_pages: int
    Has_next: bool
    Has_previous: bool
    Items_on_page: int
    Filters: Optional[Dict[str, Any]] = None


class TotalMetadata(BaseModel):
    """Total count metadata for responses"""

    TotalItems: int


class StandardResponse(BaseModel, Generic[T, M]):
    """Standard API response"""

    Success: bool
    Message: str
    Data: T
    Metadata: Optional[M] = None


class ErrorResponse(BaseModel):
    """Standard error response"""

    Success: bool = False
    Message: str
    Details: Optional[Any] = None
    Error_code: Optional[str] = None


RESPONSE_UNAUTHORIZED: dict = {
    401: {"description": "Unauthorized", "model": ErrorResponse}
}

RESPONSE_FORBIDDEN: dict = {403: {"description": "Forbidden", "model": ErrorResponse}}

RESPONSE_NOT_FOUND: dict = {404: {"description": "Not Found", "model": ErrorResponse}}

RESPONSE_CONFLICT: dict = {409: {"description": "Conflict", "model": ErrorResponse}}

RESPONSE_VALIDATION: dict = {
    422: {"description": "Validation Error", "model": ErrorResponse}
}

RESPONSE_RATE_LIMIT: dict = {
    429: {"description": "Too Many Requests", "model": ErrorResponse}
}

RESPONSE_INTERNAL_ERROR: dict = {
    500: {"description": "Internal server error", "model": ErrorResponse}
}

RESPONSE_NO_CONTENT: dict = {204: {"description": "No Content"}}


RESPONSES_DEFAULT: dict = {
    **RESPONSE_RATE_LIMIT,
    **RESPONSE_INTERNAL_ERROR,
}

RESPONSES_VALIDATION: dict = {
    **RESPONSE_VALIDATION,
}

RESPONSES_PROTECTED: dict = {
    **RESPONSE_UNAUTHORIZED,
    **RESPONSES_DEFAULT,
}

RESPONSE_CSRF_ERROR: dict = {**RESPONSE_FORBIDDEN}

RESPONSE_TWOFA_REQUIRED: dict = {
    202: {"description": "Accepted", "model": StandardResponse}
}

RESPONSE_TWOFA_ERROR: dict = {
    **RESPONSE_CONFLICT,
    **RESPONSES_PROTECTED,
}

RESPONSES_DELETE: dict = {
    **RESPONSE_NO_CONTENT,
    **RESPONSE_UNAUTHORIZED,
    **RESPONSE_NOT_FOUND,
    **RESPONSES_DEFAULT,
}
