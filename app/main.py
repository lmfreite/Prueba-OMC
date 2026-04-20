from contextlib import asynccontextmanager
import uvicorn
from dotenv import load_dotenv
from fastapi import APIRouter, FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from scalar_fastapi import Theme, get_scalar_api_reference
from app.core.settings import settings

from app.core.response_handler import ResponseHandler, handle_errors
from app.db.init_db import close_db, init_db
from app.middleware.session_expiration import SessionExpirationMiddleware
from app.schemas.response import RESPONSES_VALIDATION
from app.api.v1.api import router

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    print("Database connection initialized")
    yield
    # Shutdown
    await close_db()
    print("Database connection closed")


app = FastAPI(
    title=settings.APP_NAME,
    description="API Template",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin.strip()
        for origin in settings.CORS_ALLOWED_ORIGINS.split(",")
        if origin.strip()
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=500)

app.add_middleware(SessionExpirationMiddleware)

app.include_router(router, prefix="/api/v1", responses=RESPONSES_VALIDATION)

router = APIRouter()


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(request, exc: RequestValidationError):
    """Return validation errors using the standardized API error envelope."""
    return ResponseHandler.error_response(
        message="Validation error",
        status_code=422,
        details=exc.errors(),
        error_code="VALIDATION_ERROR",
    )


@app.get("/")
async def root():
    """Root endpoint with basic API information"""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": "1.0.0",
        "docs": "/scalar",
        "environment": settings.APP_ENV,
        "status": "running",
    }


@app.get("/health")
@handle_errors
async def health_check():
    """Basic health check"""
    return ResponseHandler.success(
        data={
            "service": f"{settings.APP_NAME}",
            "version": "1.0.0",
            "environment": settings.APP_ENV,
            "status": "healthy",
        },
        message="Service is healthy and running",
    )


@app.get("/scalar", include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=app.title,
        show_sidebar=True,
        hide_models=False,
        dark_mode=True,
        integration="fastapi",
        theme=Theme.BLUE_PLANET,
        hide_dark_mode_toggle=True,
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
