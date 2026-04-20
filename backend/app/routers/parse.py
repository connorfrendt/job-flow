from fastapi import APIRouter, HTTPException

from ..config import settings
from ..schemas.parse import ParsedJob, ParseRequest
from ..services.parser import parse_job_description

router = APIRouter(prefix="/api/parse", tags=["parse"])


@router.post("", response_model=ParsedJob)
async def parse_job(payload: ParseRequest):
    if not settings.anthropic_api_key:
        raise HTTPException(status_code=503, detail="ANTHROPIC_API_KEY not configured")
    if not payload.text.strip():
        raise HTTPException(status_code=422, detail="text cannot be empty")
    return await parse_job_description(payload.text)