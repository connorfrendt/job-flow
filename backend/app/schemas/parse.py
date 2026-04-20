from typing import List, Optional
from pydantic import BaseModel


class ParseRequest(BaseModel):
    text: str


class ParsedJob(BaseModel):
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    url: Optional[str] = None
    description: Optional[str] = None
    skills_mentioned: List[str] = []