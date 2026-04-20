from typing import Optional

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import SourceType
from app.repository.leads import LeadRepository
from app.schemas.leads import LeadCreate, LeadUpdate


def validate_source(source: str):
    try:
        SourceType(source)
    except Exception:
        raise HTTPException(status_code=422, detail="Fuente no válida")

class LeadService:
    @staticmethod
    async def create(db: AsyncSession, lead_in: LeadCreate):
        # Email único
        existing = await LeadRepository.get_by_email(db, lead_in.email)
        if existing is not None:
            raise HTTPException(status_code=409, detail="El email ya existe")
        # Normalizar source a string
        source_str = str(lead_in.source.value) if hasattr(lead_in.source, "value") else str(lead_in.source)
        validate_source(source_str)
        # Asegurar que el model_dump usa el valor string
        data = lead_in.model_dump()
        data["source"] = source_str
        obj = await LeadRepository.create(db, data)
        return obj

    @staticmethod
    async def update(db: AsyncSession, lead_id: int, lead_in: LeadUpdate):
        data = lead_in.model_dump(exclude_unset=True)
        if "email" in data:
            existe = await LeadRepository.get_by_email(db, data["email"])
            if existe is not None and getattr(existe, "id", None) != lead_id:
                raise HTTPException(status_code=409, detail="El email ya existe")
        if "source" in data and data["source"] is not None:
            source_str = str(data["source"].value) if hasattr(data["source"], "value") else str(data["source"])
            validate_source(source_str)
            data["source"] = source_str
        obj = await LeadRepository.update(db, lead_id, data)
        if obj is None:
            raise HTTPException(status_code=404, detail="Lead no encontrado")
        return obj

    @staticmethod
    async def get(db: AsyncSession, lead_id: int):
        obj = await LeadRepository.get(db, lead_id)
        if not obj:
            raise HTTPException(status_code=404, detail="Lead no encontrado")
        return obj

    @staticmethod
    async def list(
        db: AsyncSession,
        page: int = 1,
        page_size: int = 10,
        source: Optional[str] = None,
        name: Optional[str] = None,
        email: Optional[str] = None,
    ):
        from app.schemas.leads import LeadOut
        from app.schemas.response import PaginationMetadata
        skip = (page - 1) * page_size
        limit = page_size
        items, total_items = await LeadRepository.list(db, skip=skip, limit=limit, source=source, name=name, email=email)
        items = [LeadOut.from_orm(obj) for obj in items]
        total_pages = (total_items + page_size - 1) // page_size if page_size else 1
        has_next = page * page_size < total_items
        has_prev = page > 1
        filters = {}
        if source: filters['source'] = source
        if name: filters['name'] = name
        if email: filters['email'] = email
        metadata = PaginationMetadata(
            Page=page,
            Limit=page_size,
            Total_items=total_items,
            Total_pages=total_pages,
            Has_next=has_next,
            Has_previous=has_prev,
            Items_on_page=len(items),
            Filters=filters or None
        )
        return items, metadata

    @staticmethod
    async def delete(db: AsyncSession, lead_id: int):
        ok = await LeadRepository.soft_delete(db, lead_id)
        if not ok:
            raise HTTPException(status_code=404, detail="Lead no encontrado")
        return

    @staticmethod
    async def stats(db: AsyncSession):
        return await LeadRepository.get_stats(db)
