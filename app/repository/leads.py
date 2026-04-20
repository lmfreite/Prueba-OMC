from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.leads import Leads


class LeadRepository:
    @staticmethod
    async def create(db: AsyncSession, data: dict) -> Leads:
        lead = Leads(**data)
        db.add(lead)
        await db.flush()
        return lead

    @staticmethod
    async def get_by_email(db: AsyncSession, email: str) -> Optional[Leads]:
        query = select(Leads).where(and_(Leads.email == email, Leads.deleted_at.is_(None)))
        res = await db.execute(query)
        return res.scalars().first()

    @staticmethod
    async def get(db: AsyncSession, lead_id: int) -> Optional[Leads]:
        query = select(Leads).where(and_(Leads.id == lead_id, Leads.deleted_at.is_(None)))
        res = await db.execute(query)
        return res.scalars().first()

    @staticmethod
    async def list(
        db: AsyncSession, skip: int = 0, limit: int = 20, 
        source: Optional[str] = None, name: Optional[str] = None, email: Optional[str] = None
    ) -> tuple[list[Leads], int]:
        filters = [Leads.deleted_at == None]
        if source:
            filters.append(Leads.source == source)
        if name:
            filters.append(Leads.name.ilike(f"%{name}%"))
        if email:
            filters.append(Leads.email.ilike(f"%{email}%"))
        # Total count
        total_q = select(func.count()).where(*filters)
        total_res = await db.execute(total_q)
        total_count = total_res.scalar_one() or 0
        # Items paginados
        q = select(Leads).where(*filters).offset(skip).limit(limit)
        res = await db.execute(q)
        items = list(res.scalars().all())
        return items, total_count


    @staticmethod
    async def update(db: AsyncSession, lead_id: int, data: dict) -> Optional[Leads]:
        query = select(Leads).where(and_(Leads.id == lead_id, Leads.deleted_at.is_(None)))
        res = await db.execute(query)
        lead = res.scalars().first()
        if not lead:
            return None
        for k, v in data.items():
            setattr(lead, k, v)
        await db.flush()
        return lead

    @staticmethod
    async def soft_delete(db: AsyncSession, lead_id: int) -> bool:
        query = select(Leads).where(and_(Leads.id == lead_id, Leads.deleted_at.is_(None)))
        res = await db.execute(query)
        lead = res.scalars().first()
        if not lead:
            return False
        setattr(lead, "deleted_at", datetime.now(timezone.utc))
        await db.flush()
        return True

    @staticmethod
    async def get_stats(db: AsyncSession) -> Dict[str, Any]:
        # Total activos
        total_query = select(func.count()).where(Leads.deleted_at.is_(None))
        total = (await db.execute(total_query)).scalar()
        # Conteo agrupado fuente
        fuente_query = select(Leads.source, func.count()).where(Leads.deleted_at.is_(None)).group_by(Leads.source)
        source_count = {row[0].value: row[1] for row in (await db.execute(fuente_query)).all()}
        # Promedio presupuesto
        avg_query = select(func.avg(Leads.budget)).where(Leads.deleted_at.is_(None))
        budget_avg = (await db.execute(avg_query)).scalar()
        # Últimos 7 días
        since = datetime.now(timezone.utc) - timedelta(days=7)
        count_7_query = select(func.count()).where(and_(Leads.deleted_at.is_(None), Leads.created_at >= since))
        created_last_7_days = (await db.execute(count_7_query)).scalar()
        return {
            "total_active": total,
            "source_count": source_count,
            "budget_avg": budget_avg,
            "created_last_7_days": created_last_7_days,
        }
