from datetime import datetime, timedelta, timezone
import time
from functools import lru_cache
from secrets import compare_digest
from typing import Any, Optional, Union

import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
from passlib.context import CryptContext

from app.core.settings import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def secure_compare(a: str, b: str) -> bool:
    """Compara en tiempo constante para reducir riesgo de timing attacks."""
    return compare_digest(
        a.encode() if isinstance(a, str) else a,
        b.encode() if isinstance(b, str) else b,
    )
    
_jwt_settings_cache: dict = {}
_jwt_settings_cache_ts: float = 0.0
_JWT_SETTINGS_TTL: float = 300.0  # 5 minutos


def invalidate_jwt_cache() -> None:
    """Force-invalidate the JWT settings cache. Call after rotating JWT_SECRET_KEY."""
    global _jwt_settings_cache, _jwt_settings_cache_ts
    _jwt_settings_cache = {}
    _jwt_settings_cache_ts = 0.0


@lru_cache(maxsize=1)
def get_jwt_settings() -> dict[str, Union[str, float]]:
    """Retorna configuracion JWT cacheada para evitar lecturas repetidas."""
    global _jwt_settings_cache, _jwt_settings_cache_ts
    if (
        not _jwt_settings_cache
        or (time.monotonic() - _jwt_settings_cache_ts) > _JWT_SETTINGS_TTL
    ):
        _jwt_settings_cache = {
            "secret_key": settings.JWT_SECRET_KEY,
            "algorithm": settings.JWT_ALGORITHM,
            "expire_hours": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES / 60,
            "refresh_expire_days": settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS,
            "audience": settings.JWT_AUDIENCE,
            "issuer": settings.JWT_ISSUER,
        }
        _jwt_settings_cache_ts = time.monotonic()
    return _jwt_settings_cache



def hash_password(password: str) -> str:
    """Genera hash seguro de una contrasena en texto plano."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Valida una contrasena en texto plano contra su hash persistido."""
    return pwd_context.verify(plain_password, password_hash)


def create_access_token(
    subject: Union[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """Crea JWT de acceso con claims de seguridad basicos."""
    jwt_conf = get_jwt_settings()
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(hours=float(jwt_conf["expire_hours"]))

    payload = {
        "sub": str(subject),
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "iss": jwt_conf["issuer"],
        "aud": jwt_conf["audience"],
        "type": "access",
    }
    return jwt.encode(
        payload,
        str(jwt_conf["secret_key"]),
        algorithm=str(jwt_conf["algorithm"]),
    )


def verify_token(token: str) -> str:
    """
    Verify and decode JWT token.
    Returns user_id.
    Raises InvalidTokenError or ExpiredSignatureError on failure.
    """
    jwt_conf = get_jwt_settings()
    secret_key = str(jwt_conf["secret_key"])
    algorithm = str(jwt_conf["algorithm"])
    audience = str(jwt_conf["audience"])
    issuer = str(jwt_conf["issuer"])
    try:
        payload = jwt.decode(
            token,
            secret_key,
            algorithms=[algorithm],
            audience=audience,
            issuer=issuer,
        )

        # Validate token type
        token_type = payload.get("type")
        if not secure_compare(token_type or "", "access"):
            raise InvalidTokenError("Invalid token type")

        # Validate timestamp logic
        iat = payload.get("iat")
        exp = payload.get("exp")

        if iat and exp:
            if iat >= exp:
                raise InvalidTokenError(
                    "Invalid token: issued time cannot be greater than or equal to expiration time"
                )

            now = int(datetime.now(timezone.utc).timestamp())
            if iat > now:
                raise InvalidTokenError("Invalid token: issued time is in the future")

        user_id = payload.get("sub")
        if user_id is None:
            raise InvalidTokenError("Missing subject claim")

        return user_id

    except ExpiredSignatureError:
        raise ExpiredSignatureError("Token has expired")
    except InvalidTokenError:
        raise InvalidTokenError("Invalid token")



def get_current_user_from_cookie(request) -> Optional[str]:
    """Extrae usuario autenticado desde cookie HttpOnly si existe y es valida."""
    token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        return verify_token(token)
    except Exception:
        return None
