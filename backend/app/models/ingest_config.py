import uuid
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from ..database import Base


class IngestConfig(Base):
    __tablename__ = "ingest_config"

    id               = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    keywords         = Column(String(255), nullable=False)
    location         = Column(String(255))
    country          = Column(String(10), default="us")
    max_pages        = Column(Integer, default=2)
    results_per_page = Column(Integer, default=50)
    created_at       = Column(DateTime, server_default=func.now())
    updated_at       = Column(DateTime, server_default=func.now(), onupdate=func.now())