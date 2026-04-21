from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.job import Job
from ..models.profile import Profile
from ..schemas.job import JobCreate, JobResponse, JobUpdate, StarUpdate, StatusUpdate
from ..config import settings
from ..services.scoring import compute_fit, compute_fit_ai

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.get("", response_model=List[JobResponse])
async def list_jobs(
    status: Optional[str] = Query(None),
    starred: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(Job)
    if status:
        query = query.filter(Job.status == status)
    if starred is not None:
        query = query.filter(Job.starred == starred)
    if search:
        term = f"%{search}%"
        query = query.filter(
            or_(
                Job.title.ilike(term),
                Job.company.ilike(term),
                Job.location.ilike(term),
            )
        )
    return query.order_by(Job.date_found.desc()).all()


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: UUID, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.post("", response_model=JobResponse, status_code=201)
async def create_job(payload: JobCreate, db: Session = Depends(get_db)):
    job = Job(**payload.model_dump())

    profile = db.query(Profile).first()
    if profile:
        score, reasons = compute_fit(job, profile)
        if score >= 40 and settings.anthropic_api_key:
            score, reasons = await compute_fit_ai(job, profile)
        job.fit_score = score
        job.fit_reasons = reasons

    db.add(job)
    db.commit()
    db.refresh(job)
    return job


@router.put("/{job_id}", response_model=JobResponse)
async def update_job(job_id: UUID, payload: JobUpdate, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(job, field, value)
    db.commit()
    db.refresh(job)
    return job


@router.delete("/{job_id}", status_code=204)
async def delete_job(job_id: UUID, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    db.delete(job)
    db.commit()


@router.patch("/{job_id}/status", response_model=JobResponse)
async def update_status(job_id: UUID, payload: StatusUpdate, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    job.status = payload.status
    db.commit()
    db.refresh(job)
    return job


@router.patch("/{job_id}/star", response_model=JobResponse)
async def toggle_star(job_id: UUID, payload: StarUpdate, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    job.starred = payload.starred
    db.commit()
    db.refresh(job)
    return job