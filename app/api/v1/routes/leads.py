from typing import List, Optional
from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.leads import LeadCreate, LeadOut, LeadStats, LeadUpdate
from app.schemas.response import PaginationMetadata, StandardResponse
from app.service.leads import LeadService

router = APIRouter()

@router.post("/leads", response_model=StandardResponse[LeadOut, None], status_code=status.HTTP_201_CREATED)
async def create_lead(lead: LeadCreate, db: AsyncSession = Depends(get_db)):
    obj = await LeadService.create(db, lead)
    return StandardResponse[
    LeadOut, None
    ](
    Success=True,
    Message="Lead creado correctamente",
    Data=LeadOut.from_orm(obj),
    Metadata=None
    )

@router.get("/leads", response_model=StandardResponse[List[LeadOut], PaginationMetadata])
async def list_leads(
db: AsyncSession = Depends(get_db),
Page: int = Query(1, ge=1),
Page_size: int = Query(10, ge=1, le=100),
source: Optional[str] = Query(None),
name: Optional[str] = Query(None),
email: Optional[str] = Query(None),
):
    items, metadata = await LeadService.list(db, page=Page, page_size=Page_size, source=source, name=name, email=email)
    return StandardResponse[
    List[LeadOut], PaginationMetadata
    ](
    Success=True,
    Message="Listado de leads",
    Data=items,
    Metadata=metadata
    )


@router.get("/leads/stats", response_model=StandardResponse[LeadStats, None])
async def leads_stats(db: AsyncSession = Depends(get_db)):
    from app.schemas.leads import LeadStats
    stats_dict = await LeadService.stats(db)
    stats = LeadStats(**stats_dict)
    return StandardResponse[
        LeadStats, None
    ](
        Success=True,
        Message="Estadísticas de leads",
        Data=stats,
        Metadata=None
    )

@router.get("/leads/{lead_id}", response_model=StandardResponse[LeadOut, None])
async def get_lead(
lead_id: int = Path(..., gt=0),
db: AsyncSession = Depends(get_db),
):
    obj = await LeadService.get(db, lead_id)
    return StandardResponse[
    LeadOut, None
    ](
    Success=True,
    Message="Lead obtenido correctamente",
    Data=LeadOut.from_orm(obj),
    Metadata=None
    )

@router.patch("/leads/{lead_id}", response_model=StandardResponse[LeadOut, None])
async def update_lead(
    lead: LeadUpdate,
    lead_id: int = Path(..., gt=0),
    db: AsyncSession = Depends(get_db),
):
    obj = await LeadService.update(db, lead_id, lead)
    return StandardResponse[
        LeadOut, None
    ](
        Success=True,
        Message="Lead actualizado correctamente",
        Data=LeadOut.model_validate(obj),
        Metadata=None
    )

@router.delete("/leads/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lead(
    lead_id: int = Path(..., gt=0),
    db: AsyncSession = Depends(get_db),
):
    await LeadService.delete(db, lead_id)
    return
