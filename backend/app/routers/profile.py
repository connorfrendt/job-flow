from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.profile import Profile
from ..schemas.profile import ProfileResponse, ProfileUpdate

router = APIRouter(prefix="/api/profile", tags=["profile"])


@router.get("", response_model=Optional[ProfileResponse])
async def get_profile(db: Session = Depends(get_db)):
    return db.query(Profile).first()


@router.put("", response_model=ProfileResponse)
async def upsert_profile(payload: ProfileUpdate, db: Session = Depends(get_db)):
    profile = db.query(Profile).first()
    if profile is None:
        profile = Profile(**payload.model_dump())
        db.add(profile)
    else:
        for field, value in payload.model_dump().items():
            setattr(profile, field, value)
    db.commit()
    db.refresh(profile)
    return profile