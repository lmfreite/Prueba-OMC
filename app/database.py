from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.settings import settings


class Base(DeclarativeBase):
    """Base declarativa para todos los modelos ORM."""


engine = create_engine(settings.DATABASE_URL, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def get_db() -> Generator[Session, None, None]:
    """Entrega una sesion de base de datos por request y la cierra al finalizar."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
