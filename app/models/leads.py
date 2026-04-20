from app.models.base import BaseModel
from sqlalchemy import Column, String, Float, Integer, UniqueConstraint, Enum
from app.models.enums import SourceType


class Leads(BaseModel):
    """Modelo de datos para representar un lead."""
    __tablename__ = "leads"
    __table_args__ = (
        UniqueConstraint("email", name="uq_leads_email"),
    )

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True, index=True)
    phone = Column(String, nullable=True)
    source = Column(Enum(SourceType), nullable=False)
    product_interest = Column(String, nullable=True)
    budget = Column(Float, nullable=True)