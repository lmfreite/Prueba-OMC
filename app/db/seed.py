from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security_simple import hash_password
from app.models.user import User
from app.core.settings import settings


async def seed_database(session: AsyncSession) -> None:
    """Ejecuta seed minimo creando el usuario por defecto si no existe."""
    result = await session.execute(
        select(User).where(User.username == settings.DEFAULT_USERNAME)
    )
    default_user = result.scalar_one_or_none()

    if default_user:
        return

    session.add(
        User(
            username=settings.DEFAULT_USERNAME,
            password_hash=hash_password(settings.DEFAULT_PASSWORD),
        )
    )
    await session.commit()
