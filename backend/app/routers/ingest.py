from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import httpx

from ..config import settings
from ..database import get_db
from ..models.ingest_config import IngestConfig
from ..schemas.ingest import IngestConfigResponse, IngestConfigUpdate, IngestResult
from ..services.ingest import run_ingest

ADZUNA_BASE = "https://api.adzuna.com/v1/api/jobs"

router = APIRouter(prefix="/api/ingest", tags=["ingest"])


@router.get("/config", response_model=Optional[IngestConfigResponse])
async def get_config(db: Session = Depends(get_db)):
    return db.query(IngestConfig).first()


@router.put("/config", response_model=IngestConfigResponse)
async def upsert_config(payload: IngestConfigUpdate, db: Session = Depends(get_db)):
    config = db.query(IngestConfig).first()
    if config is None:
        config = IngestConfig(**payload.model_dump())
        db.add(config)
    else:
        for field, value in payload.model_dump().items():
            setattr(config, field, value)
    db.commit()
    db.refresh(config)
    return config


@router.post("/trigger", response_model=IngestResult)
async def trigger_ingest(db: Session = Depends(get_db)):
    if not settings.adzuna_app_id or not settings.adzuna_app_key:
        raise HTTPException(status_code=503, detail="Adzuna credentials not configured")

    config = db.query(IngestConfig).first()
    if not config:
        raise HTTPException(
            status_code=400,
            detail="No ingest config saved. Set your search criteria first.",
        )

    config_dict = {
        "keywords":         config.keywords,
        "location":         config.location or "",
        "country":          config.country,
        "max_pages":        config.max_pages,
        "results_per_page": config.results_per_page,
    }

    return await run_ingest(config_dict, db)


@router.get("/test")
async def test_adzuna(db: Session = Depends(get_db)):
    """Return raw Adzuna response for debugging."""
    if not settings.adzuna_app_id or not settings.adzuna_app_key:
        raise HTTPException(status_code=503, detail="Adzuna credentials not configured")

    config = db.query(IngestConfig).first()
    if not config:
        raise HTTPException(status_code=400, detail="No ingest config saved.")

    url = f"{ADZUNA_BASE}/{config.country}/search/1"
    params = {
        "app_id": settings.adzuna_app_id,
        "app_key": settings.adzuna_app_key,
        "what": config.keywords,
        "results_per_page": 5,
        "content-type": "application/json",
    }
    if config.location:
        params["where"] = config.location

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(url, params=params)

    return {
        "status_code": resp.status_code,
        "url_called": str(resp.url),
        "body": resp.json() if resp.headers.get("content-type", "").startswith("application/json") else resp.text,
    }