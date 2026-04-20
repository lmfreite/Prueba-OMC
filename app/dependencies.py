from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.response_handler import ResponseHandler
from app.core.security_simple import get_current_user_from_cookie
from app.db.session import get_db
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.services.llm.base import LLMService
from app.services.llm.openai_client import OpenAIClient


async def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    """Crea el servicio de autenticacion con su repositorio asociado."""
    return AuthService(UserRepository(db))


def get_current_user(
    request: Request,
) -> str:
    """Obtiene usuario autenticado exclusivamente desde cookie HttpOnly."""
    cookie_user = get_current_user_from_cookie(request)
    if cookie_user:
        return cookie_user

    raise ResponseHandler.unauthorized("Token de autenticacion requerido")


async def get_current_active_user(
    request: Request,
    service: AuthService = Depends(get_auth_service),
) -> User:
    """Obtiene y valida en base de datos el usuario representado por la cookie."""
    subject = get_current_user(request)
    return await service.get_user_by_session_subject(subject)


def get_llm_service() -> LLMService:
    """Retorna la implementacion concreta del servicio LLM (OpenAI)."""
    return OpenAIClient()
