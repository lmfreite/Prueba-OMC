from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr
from app.models.enums import SourceType

class LeadBase(BaseModel):
    name: str = Field(..., min_length=2)
    email: EmailStr
    phone: Optional[str] = None
    source: SourceType
    product_interest: Optional[str] = None
    budget: Optional[float] = Field(None, gt=0)

class LeadCreate(LeadBase):
    pass

class LeadUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2)
    phone: Optional[str] = None
    source: Optional[SourceType] = None
    product_interest: Optional[str] = None
    budget: Optional[float] = Field(None, gt=0)
    
class LeadOut(LeadBase):
    id: int

    class Config:
        from_attributes = True

class LeadStats(BaseModel):
    total_active: int
    source_count: dict
    budget_avg: Optional[float]
    created_last_7_days: int

class LeadAISummaryRequest(BaseModel):
    source: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
