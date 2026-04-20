import uuid
from typing import Optional

from fastapi import Request, Response, status

from app.core.response_handler import ResponseHandler
from app.core.security_simple import (create_access_token,
                                      get_current_user_from_cookie,
                                      hash_password, verify_password)
from app.core.settings import settings
from app.repositories.user_repository import UserRepository


class AuthService:
    """Gestiona el ciclo de autenticacion y registro de usuarios."""

    def __init__(self, repository: UserRepository) -> None:
        self.repository = repository

    async def register_user(self, username: str, password: str) -> None:
        """Registra un usuario nuevo asegurando unicidad de username."""
        user = await self.repository.get_by_username(username)
        if user:
            raise ResponseHandler.error(
                message="El usuario ya existe",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        password_hash = hash_password(password)
        await self.repository.create(username=username, password_hash=password_hash)

    async def login(self, username: str, password: str) -> str:
        """Valida credenciales y retorna un JWT con el id del usuario en sub."""
        user = await self.repository.get_by_username(username)
        if not user or not verify_password(password, user.password_hash):
            raise ResponseHandler.unauthorized("Credenciales invalidas")

        return create_access_token(subject=user.id)

    async def login_user_session(
        self,
        response: Response,
        username: str,
        password: str,
        secure: bool = False,
    ) -> None:
        """Autentica usuario y crea cookie de sesion HttpOnly."""
        token = await self.login(username=username, password=password)
        self.set_auth_cookie(response=response, token=token, secure=secure)

    def logout_user_session(self, response: Response, secure: bool = False) -> None:
        """Cierra sesion eliminando la cookie de autenticacion."""
        self.clear_auth_cookie(response=response, secure=secure)

    async def get_user_by_session_subject(self, subject: str):
        """Resuelve y valida el usuario usando el subject (UUID) del JWT."""
        try:
            user_id = uuid.UUID(subject)
        except ValueError as exc:
            raise ResponseHandler.unauthorized("Sesion invalida") from exc

        user = await self.repository.get_by_id(user_id)
        if not user:
            raise ResponseHandler.unauthorized("Sesion invalida")
        return user

    @staticmethod
    def set_auth_cookie(response: Response, token: str, secure: bool = False) -> None:
        """Setea la cookie HttpOnly de autenticacion."""
        response.set_cookie(
            key="access_token",
            value=token,
            max_age=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            httponly=True,
            secure=secure,
            samesite=settings.COOKIE_SAMESITE,
            path="/",
        )

    @staticmethod
    def has_auth_cookie(request: Request) -> bool:
        """Verifica si existe cookie de autenticacion en la request."""
        token = request.cookies.get("access_token")
        return bool(token and token.strip())

    @staticmethod
    def get_user_from_session(request: Request) -> Optional[str]:
        """Obtiene el usuario autenticado a partir de la cookie de sesion."""
        return get_current_user_from_cookie(request)

    @staticmethod
    def clear_auth_cookie(response: Response, secure: bool = False) -> None:
        """Elimina la cookie de autenticacion para forzar nuevo login."""
        response.delete_cookie(
            key="access_token",
            httponly=True,
            secure=secure,
            samesite=settings.COOKIE_SAMESITE,
            path="/",
        )
