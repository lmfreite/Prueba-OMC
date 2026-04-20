from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security_simple import hash_password
from app.models.user import User
from app.models.leads import Leads
from app.models.enums import SourceType
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


async def seed_leads(session: AsyncSession) -> None:
    """Inserta 10 leads de ejemplo si la tabla está vacía."""
    result = await session.execute(select(Leads))
    existing = result.scalars().first()

    if existing:
        return

    sample_leads = [
        Leads(
            name="Carlos Ramírez",
            email="carlos.ramirez@example.com",
            phone="+573001234567",
            source=SourceType.INSTAGRAM,
            product_interest="Camisetas sublimadas",
            budget=150000.0,
        ),
        Leads(
            name="Ana Gómez",
            email="ana.gomez@example.com",
            phone="+573109876543",
            source=SourceType.FACEBOOK,
            product_interest="Tazas personalizadas",
            budget=80000.0,
        ),
        Leads(
            name="Luis Martínez",
            email="luis.martinez@example.com",
            phone="+573204567890",
            source=SourceType.LANDING_PAGE,
            product_interest="Gorras bordadas",
            budget=200000.0,
        ),
        Leads(
            name="María Torres",
            email="maria.torres@example.com",
            phone="+573315678901",
            source=SourceType.REFERRED,
            product_interest="Bolsas ecológicas",
            budget=120000.0,
        ),
        Leads(
            name="Juan Pérez",
            email="juan.perez@example.com",
            phone=None,
            source=SourceType.OTHER,
            product_interest="Libretas personalizadas",
            budget=60000.0,
        ),
        Leads(
            name="Sofía Herrera",
            email="sofia.herrera@example.com",
            phone="+573426789012",
            source=SourceType.INSTAGRAM,
            product_interest="Almohadas sublimadas",
            budget=175000.0,
        ),
        Leads(
            name="Diego Vargas",
            email="diego.vargas@example.com",
            phone="+573537890123",
            source=SourceType.FACEBOOK,
            product_interest="Cuadros decorativos",
            budget=300000.0,
        ),
        Leads(
            name="Valentina Cruz",
            email="valentina.cruz@example.com",
            phone="+573648901234",
            source=SourceType.LANDING_PAGE,
            product_interest="Camisetas sublimadas",
            budget=90000.0,
        ),
        Leads(
            name="Andrés Morales",
            email="andres.morales@example.com",
            phone="+573759012345",
            source=SourceType.REFERRED,
            product_interest="Termos personalizados",
            budget=250000.0,
        ),
        Leads(
            name="Camila Jiménez",
            email="camila.jimenez@example.com",
            phone=None,
            source=SourceType.OTHER,
            product_interest="Puzzles personalizados",
            budget=110000.0,
        ),
    ]

    session.add_all(sample_leads)
    await session.commit()
    print(f"Seed: {len(sample_leads)} leads insertados correctamente.")
