from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


class IngestConfigUpdate(BaseModel):
    keywords:         str
    location:         Optional[str] = None
    country:          str = "us"
    max_pages:        int = Field(default=2, ge=1, le=10)
    results_per_page: int = Field(default=50, ge=10, le=50)


class IngestConfigResponse(IngestConfigUpdate):
    id:         UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class IngestResult(BaseModel):
    fetched:        int
    skipped_dedup:  int
    skipped_filter: int
    saved:          int