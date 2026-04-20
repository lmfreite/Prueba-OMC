"""Esquemas expuestos por la API esencial de la prueba tecnica."""

from app.schemas.auth_simple import LoginRequest, RegisterRequest
from app.schemas.response import StandardResponse, ErrorResponse

__all__ = [
    "RegisterRequest",
    "LoginRequest",
    "StandardResponse",
    "ErrorResponse",
]
