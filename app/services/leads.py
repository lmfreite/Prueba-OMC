# app/services/leads.py
from typing import Optional

from fastapi import HTTPException
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.leads import Leads
from app.repository.leads import LeadRepository
from app.schemas.leads import LeadCreate, LeadOut, LeadUpdate
from app.schemas.response import PaginationMetadata
from app.services.llm.base import LLMService
from app.services.llm.openai_client import LLMServiceError
from app.utils.leads import validate_source, resolve_source_str, serialize_lead


class LeadService:

    @staticmethod
    async def create(db: AsyncSession, lead_in: LeadCreate) -> Leads:
        existing = await LeadRepository.get_by_email(db, lead_in.email)
        if existing is not None:
            raise HTTPException(status_code=409, detail="El email ya está registrado.")

        source_str = resolve_source_str(lead_in.source)
        validate_source(source_str)

        data = lead_in.model_dump()
        data["source"] = source_str

        return await LeadRepository.create(db, data)

    @staticmethod
    async def update(db: AsyncSession, lead_id: int, lead_in: LeadUpdate) -> Leads:
        data = lead_in.model_dump(exclude_unset=True)

        if "email" in data:
            existing = await LeadRepository.get_by_email(db, data["email"])
            if existing is not None and getattr(existing, "id", None) != lead_id:
                raise HTTPException(status_code=409, detail="El email ya está registrado.")

        if "source" in data and data["source"] is not None:
            source_str = resolve_source_str(data["source"])
            validate_source(source_str)
            data["source"] = source_str

        obj = await LeadRepository.update(db, lead_id, data)
        if obj is None:
            raise HTTPException(status_code=404, detail="Lead no encontrado.")

        return obj

    @staticmethod
    async def get(db: AsyncSession, lead_id: int) -> Leads:
        obj = await LeadRepository.get(db, lead_id)
        if not obj:
            raise HTTPException(status_code=404, detail="Lead no encontrado.")
        return obj

    @staticmethod
    async def list(
        db: AsyncSession,
        page: int = 1,
        page_size: int = 10,
        source: Optional[str] = None,
        name: Optional[str] = None,
        email: Optional[str] = None,
    ) -> tuple[list[LeadOut], PaginationMetadata]:
        skip = (page - 1) * page_size

        items, total_items = await LeadRepository.list(
            db, skip=skip, limit=page_size,
            source=source, name=name, email=email,
        )

        items_out = [LeadOut.model_validate(obj) for obj in items]
        total_pages = (total_items + page_size - 1) // page_size if page_size else 1
        active_filters = {k: v for k, v in {"source": source, "name": name, "email": email}.items() if v}

        metadata = PaginationMetadata(
            Page=page,
            Limit=page_size,
            Total_items=total_items,
            Total_pages=total_pages,
            Has_next=page * page_size < total_items,
            Has_previous=page > 1,
            Items_on_page=len(items_out),
            Filters=active_filters or None,
        )

        return items_out, metadata

    @staticmethod
    async def delete(db: AsyncSession, lead_id: int) -> None:
        ok = await LeadRepository.soft_delete(db, lead_id)
        if not ok:
            raise HTTPException(status_code=404, detail="Lead no encontrado.")

    @staticmethod
    async def stats(db: AsyncSession) -> dict:
        return await LeadRepository.get_stats(db)

    @staticmethod
    async def ai_summary(
        db: AsyncSession,
        filtro,
        llm: LLMService,
        idioma: str = "es",
    ) -> dict:
        filters = [Leads.deleted_at.is_(None)]

        if filtro.source:
            filters.append(Leads.source == filtro.source)
        if hasattr(filtro, "date_from") and filtro.date_from:
            filters.append(Leads.created_at >= filtro.date_from)
        if hasattr(filtro, "date_to") and filtro.date_to:
            filters.append(Leads.created_at <= filtro.date_to)

        result = await db.execute(select(Leads).where(and_(*filters)))
        leads = result.scalars().all()

        if not leads:
            raise HTTPException(
                status_code=404,
                detail="No se encontraron leads con los filtros proporcionados.",
            )

        leads_data = [serialize_lead(lead) for lead in leads]

        try:
            summary = await llm.get_summary(leads_data, idioma=idioma)
        except LLMServiceError as e:
            raise HTTPException(status_code=502, detail=str(e))

        return {
            "summary": summary,
            "leads_analizados": len(leads_data),
        }