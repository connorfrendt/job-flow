from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel


class Skill(BaseModel):
    name: str
    level: str  # 'beginner' | 'intermediate' | 'advanced'


class ProfileUpdate(BaseModel):
    skills: Optional[List[Skill]] = None
    target_titles: Optional[List[str]] = None
    location: Optional[str] = None
    remote_pref: Optional[str] = None  # 'remote' | 'hybrid' | 'onsite' | 'any'
    salary_floor: Optional[int] = None
    exclusion_words: Optional[List[str]] = None


class ProfileResponse(BaseModel):
    id: UUID
    skills: Optional[List[Skill]] = None
    target_titles: Optional[List[str]] = None
    location: Optional[str] = None
    remote_pref: Optional[str] = None
    salary_floor: Optional[int] = None
    exclusion_words: Optional[List[str]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
