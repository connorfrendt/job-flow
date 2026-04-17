import uuid
from sqlalchemy import Boolean, Column, Date, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.sql import func
from ..database import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    company = Column(String(255))
    location = Column(String(255))
    salary_min = Column(Integer)
    salary_max = Column(Integer)
    url = Column(Text)
    description = Column(Text)
    source = Column(String(50), default="manual")
    status = Column(String(50), default="new_leads")

    # AI enrichment
    fit_score = Column(Integer)
    fit_reasons = Column(JSONB)
    legit_score = Column(Integer)
    legit_flags = Column(JSONB)

    # User fields
    notes = Column(Text)
    contact_name = Column(String(255))
    contact_email = Column(String(255))
    follow_up_date = Column(Date)
    starred = Column(Boolean, default=False)

    # Dedup
    adzuna_id = Column(String(100), unique=True)
    description_hash = Column(String(64))

    # Timestamps
    date_found = Column(DateTime, server_default=func.now())
    date_applied = Column(DateTime)
    date_updated = Column(DateTime, server_default=func.now(), onupdate=func.now())
    created_at = Column(DateTime, server_default=func.now())
