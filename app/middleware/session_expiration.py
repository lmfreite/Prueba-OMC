import json
from fastapi import Request
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from starlette.types import ASGIApp
from app.services import AuthService


class SessionExpirationMiddleware(BaseHTTPMiddleware):
    """Middleware for automatic session expiration handling"""

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        user_id = AuthService.get_user_from_session(request)
        has_access = AuthService.has_auth_cookie(request)

        if user_id is None and (has_access):
            secure = request.url.scheme == "https"

            logging.getLogger(__name__).warning(
                f"Expired session detected from IP: {request.client.host if request.client else 'unknown'}"
            )
            return self._clear_expired_session(
                "Session expired or invalid. Please login again.",
                request,
                secure=secure,
            )

        return await call_next(request)

    def _clear_expired_session(
        self, message: str, request: Request, secure: bool
    ) -> Response:
        """Clear expired session cookie and return error"""
        content = {
            "Success": False,
            "Message": message,
            "Data": {"session_expired": True, "action_required": "login"},
            "Error_code": "SESSION_EXPIRED",
            "Details": None,
        }
        error_response = Response(
            content=json.dumps(content),
            status_code=401,
            media_type="application/json",
        )
        AuthService.clear_auth_cookie(error_response, secure=secure)
        error_response.headers["X-Session-Status"] = "expired"
        return error_response
