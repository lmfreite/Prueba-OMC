import os
from typing import Literal

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Centraliza la configuracion de entorno de la API."""

 # Application Configuration
    APP_NAME: str
    APP_ENV: Literal["development", "staging", "production"] = "production"

    # CORS Configuration
    CORS_ALLOWED_ORIGINS: str

    # Database Configuration
    POSTGRES_DB_DEBUG: bool
    POSTGRES_DB_HOST: str
    POSTGRES_DB_PORT: int
    POSTGRES_DB_NAME: str
    POSTGRES_DB_USER: str
    POSTGRES_DB_PASSWORD: str
    POSTGRES_DB_DRIVER: str

    # Database Pool Configuration
    DB_POOL_SIZE: int = 100
    DB_POOL_MAX_OVERFLOW: int = 50
    DB_POOL_RECYCLE: int = 120
    DB_POOL_PRE_PING: bool = True

    # JWT Configuration
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int
    JWT_ISSUER: str = "omc-api.com"
    JWT_AUDIENCE: str = "omc-api-users"
    COOKIE_SECURE: bool = True
    COOKIE_SAMESITE: Literal["lax", "strict", "none"] = "none"
    
    DEFAULT_USERNAME:str
    DEFAULT_PASSWORD:str

    

    @staticmethod
    def _is_running_in_docker() -> bool:
        return os.path.exists("/.dockerenv")

    @classmethod
    def _resolve_container_host_port(cls, host: str, port: int) -> tuple[str, int]:
        """
        Resolve Docker-internal service names when running locally.
        Keeps container hostnames unchanged when running inside Docker.
        """
        if cls._is_running_in_docker():
            return host, port

        host_map = {
            "postgres": ("localhost", 5432),
        }
        return host_map.get(host, (host, port))

    @property
    def is_development(self) -> bool:
        """True only in development environment"""
        return self.APP_ENV == "development"

    @property
    def is_production(self) -> bool:
        """True only in production environment"""
        return self.APP_ENV == "production"

    @property
    def DATABASE_URL(self) -> str:
        """Build database connection URL"""
        host, port = self._resolve_container_host_port(
            self.POSTGRES_DB_HOST, self.POSTGRES_DB_PORT
        )
        return f"{self.POSTGRES_DB_DRIVER}://{self.POSTGRES_DB_USER}:{self.POSTGRES_DB_PASSWORD}@{host}:{port}/{self.POSTGRES_DB_NAME}"

    @property
    def ALEMBIC_DATABASE_URL(self) -> str:
        """Build Alembic database connection URL"""
        host, port = self._resolve_container_host_port(
            self.POSTGRES_DB_HOST, self.POSTGRES_DB_PORT
        )
        return f"postgresql+psycopg://{self.POSTGRES_DB_USER}:{self.POSTGRES_DB_PASSWORD}@{host}:{port}/{self.POSTGRES_DB_NAME}"

    @property
    def POSTGRES_DB_HOST_EFFECTIVE(self) -> str:
        host, _ = self._resolve_container_host_port(
            self.POSTGRES_DB_HOST, self.POSTGRES_DB_PORT
        )
        return host

    @property
    def POSTGRES_DB_PORT_EFFECTIVE(self) -> int:
        _, port = self._resolve_container_host_port(
            self.POSTGRES_DB_HOST, self.POSTGRES_DB_PORT
        )
        return port

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"


settings = Settings()  # type: ignore

