from sqlalchemy import Column, DateTime, func

from app.db.base_class import Base


class BaseModel(Base):
    """Base model with common audit columns"""

    __abstract__ = True

    # Audit columns
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    @property
    def IsDeleted(self) -> bool:
        """Checks if the record is marked as deleted"""
        return self.deleted_at is not None