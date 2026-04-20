from app.models.enums import SourceType
from app.models.leads import Leads

from fastapi import HTTPException

def validate_source(source: str) -> None:
    try:
        SourceType(source)
    except ValueError:
        raise HTTPException(status_code=422, detail=f"Fuente no válida: '{source}'")

def resolve_source_str(source) -> str:
    return source.value if hasattr(source, "value") else str(source)

def serialize_lead(lead: Leads) -> dict:
    return {
        "id": lead.id,
        "name": lead.name,
        "email": lead.email,
        "phone": lead.phone,
        "source": resolve_source_str(lead.source),
        "product_interest": lead.product_interest,
        "budget": lead.budget,
        "created_at": lead.created_at.isoformat() if lead.created_at is not None else None
    }
