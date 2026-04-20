from typing import Any, Optional, Dict
from functools import wraps
from fastapi.encoders import jsonable_encoder
from fastapi import HTTPException, Response, status
from fastapi.responses import JSONResponse
from app.schemas import StandardResponse, ErrorResponse
from app.core.settings import settings


class ResponseHandler:
    """Centralized handler for endpoint response management"""

    @staticmethod
    def _sanitize_for_json(value: Any) -> Any:
        if isinstance(value, BaseException):
            return str(value)
        try:
            return jsonable_encoder(value)
        except Exception:
            return str(value)

    @staticmethod
    def success(
        data: Any = None,
        message: str = "Operation successful",
        status_code: int = status.HTTP_200_OK,
        metadata: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        response: Optional[Response] = None,
    ) -> JSONResponse:
        """Standardized success response using StandardResponse schema"""
        serialized_data = ResponseHandler._sanitize_for_json(data)
        serialized_metadata = ResponseHandler._sanitize_for_json(metadata)

        response_data = StandardResponse(
            Success=True, Message=message, Data=serialized_data, Metadata=serialized_metadata
        ).model_dump(mode="json")

        json_response = JSONResponse(
            content=response_data,
            status_code=status_code,
            headers=headers or {},
        )

        if response is not None and hasattr(response, "raw_headers"):
            for header, value in response.raw_headers:
                if header.lower() == b"set-cookie":
                    json_response.headers.append("set-cookie", value.decode())

        return json_response

    @staticmethod
    def error(
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: Any = None,
        error_code: Optional[str] = None,
    ) -> HTTPException:
        """Standardized error exception using ErrorResponse schema"""

        serialized_details = ResponseHandler._sanitize_for_json(details)

        error_response = ErrorResponse(
            Success=False,
            Message=message,
            Details=serialized_details,
            Error_code=error_code,
        ).model_dump(mode="json")

        raise HTTPException(status_code=status_code, detail=error_response)

    @staticmethod
    def error_response(
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: Any = None,
        error_code: Optional[str] = None,
    ) -> JSONResponse:
        """Standardized JSON error response without raising an exception."""
        serialized_details = ResponseHandler._sanitize_for_json(details)

        error_response = ErrorResponse(
            Success=False,
            Message=message,
            Details=serialized_details,
            Error_code=error_code,
        ).model_dump(mode="json")

        return JSONResponse(
            status_code=status_code,
            content={"detail": error_response},
        )

    @staticmethod
    def server_error(
        error: Exception, custom_message: Optional[str] = None
    ) -> HTTPException:
        """Internal server error"""
        message = custom_message or "Internal server error occurred"
        details = str(error) if settings.is_development else None
        return ResponseHandler.error(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details,
            error_code="INTERNAL_SERVER_ERROR",
        )

    @staticmethod
    def unauthorized(message: str = "Authentication required") -> HTTPException:
        """Authorization error"""
        return ResponseHandler.error(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="UNAUTHORIZED",
        )

    @staticmethod
    def forbidden(message: str = "Access forbidden") -> HTTPException:
        """Permissions error"""
        return ResponseHandler.error(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="FORBIDDEN",
        )

    @staticmethod
    def not_found(message: str = "Resource not found") -> HTTPException:
        """Resource not found error"""
        return ResponseHandler.error(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="NOT_FOUND",
        )

    @staticmethod
    def conflict(message: str = "Resource already exists") -> HTTPException:
        """Conflict error - resource already exists"""
        return ResponseHandler.error(
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            error_code="CONFLICT",
        )

    @staticmethod
    def validation_error(message: str, details: Any = None) -> HTTPException:
        """Validation error"""
        return ResponseHandler.error(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details,
            error_code="VALIDATION_ERROR",
        )

    @staticmethod
    def request_too_large(
        message: str = "Request entity too large", max_size: Optional[str] = None
    ) -> HTTPException:
        """Request too large error - HTTP 413"""
        details = None
        if max_size:
            details = {"max_allowed_size": max_size}

        return ResponseHandler.error(
            message=message,
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            details=details,
            error_code="REQUEST_TOO_LARGE",
        )

    @staticmethod
    def unsupported_media_type(
        message: str = "Unsupported media type", supported_types: Optional[list] = None
    ) -> HTTPException:
        """Unsupported media type error - HTTP 415"""
        details = None
        if supported_types:
            details = {"supported_media_types": supported_types}

        return ResponseHandler.error(
            message=message,
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            details=details,
            error_code="UNSUPPORTED_MEDIA_TYPE",
        )

    @staticmethod
    def service_unavailable(
        message: str = "Service temporarily unavailable",
    ) -> HTTPException:
        """Service unavailable (useful for health checks)"""
        return ResponseHandler.error(
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error_code="SERVICE_UNAVAILABLE",
        )

    @staticmethod
    def accepted(
        data: Any = None,
        message: str = "Request accepted",
        metadata: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        response: Optional[Response] = None,
    ) -> JSONResponse:
        """Standardized 202 Accepted response using StandardResponse schema"""
        response_data = StandardResponse(
            Success=True, Message=message, Data=data, Metadata=metadata
        ).model_dump(mode="json")

        json_response = JSONResponse(
            content=response_data,
            status_code=status.HTTP_202_ACCEPTED,
            headers=headers or {},
        )

        if response is not None and hasattr(response, "raw_headers"):
            for header, value in response.raw_headers:
                if header.lower() == b"set-cookie":
                    json_response.headers.append("set-cookie", value.decode())

        return json_response


def handle_errors(func):
    """Decorator for automatic error handling in endpoints"""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except HTTPException:
            raise
        except Exception as e:
            raise ResponseHandler.server_error(e)

    return wrapper
