from fastapi import APIRouter, Depends, Response, status

from app.core.response_handler import ResponseHandler, handle_errors
from app.dependencies import get_auth_service
from app.schemas.auth_simple import LoginRequest, RegisterRequest
from app.schemas.response import RESPONSES_DEFAULT, StandardResponse
from app.services.auth_service import AuthService

router = APIRouter()


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    responses=RESPONSES_DEFAULT,
    response_model=StandardResponse[None],
)
@handle_errors
async def register(
    payload: RegisterRequest,
    service: AuthService = Depends(get_auth_service),
) :
    """Registra un usuario local para habilitar autenticacion por token."""
    await service.register_user(username=payload.username, password=payload.password)
    return ResponseHandler.success(
        message="Usuario creado correctamente",
        status_code=status.HTTP_201_CREATED,
    )


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    responses=RESPONSES_DEFAULT,
    response_model=StandardResponse[None],
)
@handle_errors
async def login(
    payload: LoginRequest,
    response: Response,
    service: AuthService = Depends(get_auth_service),
) :
    """Autentica y establece JWT solo en cookie HttpOnly."""
    await service.login_user_session(
        response=response,
        username=payload.username,
        password=payload.password,
    )

    return ResponseHandler.success(
        message="Autenticacion exitosa",
        response=response,
    )


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    responses=RESPONSES_DEFAULT,
    response_model=StandardResponse[None],
)
@handle_errors
async def logout(
    response: Response,
    service: AuthService = Depends(get_auth_service),
) :
    """Cierra sesion eliminando la cookie HttpOnly del token de acceso."""
    service.logout_user_session(response=response)
    return ResponseHandler.success(
        message="Sesion cerrada correctamente",
        response=response,
    )
