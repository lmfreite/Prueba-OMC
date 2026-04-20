import asyncpg

from app.db.seed import seed_database
from app.db.session import AsyncSessionLocal, engine
from app.services import AlembicService
from app.core.settings import settings


async def create_database_if_not_exists():
    """
    Crea la base de datos si no existe.
    """
    db_name = settings.POSTGRES_DB_NAME
    try:
        conn = await asyncpg.connect(
            user=settings.POSTGRES_DB_USER,
            password=settings.POSTGRES_DB_PASSWORD,
            host=settings.POSTGRES_DB_HOST_EFFECTIVE,
            port=settings.POSTGRES_DB_PORT_EFFECTIVE,
            database="postgres",
        )
        exists = await conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = $1", db_name
        )
        if exists:
            print(f"⛁ Database '{settings.POSTGRES_DB_NAME}' already exists")
        else:
            await conn.execute(f'CREATE DATABASE "{db_name}"')
            print(f"⛁ Database '{db_name}' created successfully")
        await conn.close()
    except Exception as e:
        print(f"❌ Error creating database '{db_name}': {e}")


async def init_db():
    """
    Inicializar la base de datos creando todas las tablas y datos iniciales
    """
    try:
        await create_database_if_not_exists()
        AlembicService.check_and_apply_migrations()
        async with AsyncSessionLocal() as session:
            await seed_database(session)
    except Exception as e:
        print(f"❌ Error inicializando la base de datos: {e}")


async def close_db() -> None:
    """Cierra el engine asincrono de SQLAlchemy."""
    await engine.dispose()
