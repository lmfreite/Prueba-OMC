from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.core.settings import settings
from typing import AsyncGenerator


engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.POSTGRES_DB_DEBUG,
    future=True,
    pool_pre_ping=settings.DB_POOL_PRE_PING,
    pool_size=settings.DB_POOL_SIZE,
    pool_recycle=settings.DB_POOL_RECYCLE,
    max_overflow=settings.DB_POOL_MAX_OVERFLOW,
)

# Crear el sessionmaker asíncrono
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


# Dependencia para obtener la sesión de base de datos
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency para obtener una sesión de base de datos asíncrona
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
