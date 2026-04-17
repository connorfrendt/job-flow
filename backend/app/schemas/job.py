from datetime import date, datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel


class FitReason(BaseModel):
    type: str   # 'pro' | 'con'
    text: str


class LegitFlag(BaseModel):
    level: str  # 'green' | 'yellow' | 'red'
    text: str


class JobCreate(BaseModel):
    title: str
    company: Optional[str] = None
    location: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    url: Optional[str] = None
    description: Optional[str] = None
    source: str = "manual"
    status: str = "new_leads"
    notes: Optional[str] = None
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    follow_up_date: Optional[date] = None
    starred: bool = False


class JobUpdate(BaseModel):
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    url: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    follow_up_date: Optional[date] = None
    starred: Optional[bool] = None


class StatusUpdate(BaseModel):
    status: str


class StarUpdate(BaseModel):
    starred: bool


class JobResponse(BaseModel):
    id: UUID
    title: str
    company: Optional[str] = None
    location: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    url: Optional[str] = None
    description: Optional[str] = None
    source: str
    status: str
    fit_score: Optional[int] = None
    fit_reasons: Optional[List[FitReason]] = None
    legit_score: Optional[int] = None
    legit_flags: Optional[List[LegitFlag]] = None
    notes: Optional[str] = None
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    follow_up_date: Optional[date] = None
    starred: bool
    adzuna_id: Optional[str] = None
    date_found: Optional[datetime] = None
    date_applied: Optional[datetime] = None
    date_updated: Optional[datetime] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
