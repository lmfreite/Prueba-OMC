from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    """Datos necesarios para registrar un usuario."""

    username: str = Field(..., min_length=3, max_length=80)
    password: str = Field(..., min_length=8, max_length=128)


class LoginRequest(BaseModel):
    """Datos necesarios para autenticarse."""

    username: str = Field(..., min_length=3, max_length=80)
    password: str = Field(..., min_length=8, max_length=128)
