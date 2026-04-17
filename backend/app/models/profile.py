import uuid
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.sql import func
from ..database import Base


class Profile(Base):
    __tablename__ = "profile"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    skills = Column(JSONB)
    target_titles = Column(JSONB)
    location = Column(String(255))
    remote_pref = Column(String(50))
    salary_floor = Column(Integer)
    exclusion_words = Column(JSONB)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
