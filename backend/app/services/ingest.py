import asyncio
import hashlib

from sqlalchemy.orm import Session

from ..config import settings
from ..models.job import Job
from ..models.profile import Profile
from .adzuna import search_jobs
from .scoring import compute_fit, compute_fit_ai


def _desc_hash(text: str) -> str:
    normalized = " ".join(text.lower().split())
    return hashlib.sha256(normalized.encode()).hexdigest()


def _map_adzuna(raw: dict) -> dict:
    """Map a raw Adzuna result to our Job field dict."""
    return {
        "adzuna_id":        str(raw.get("id", "")),
        "title":            raw.get("title", "Unknown"),
        "company":          raw.get("company", {}).get("display_name"),
        "location":         raw.get("location", {}).get("display_name"),
        "salary_min":       int(raw["salary_min"]) if raw.get("salary_min") else None,
        "salary_max":       int(raw["salary_max"]) if raw.get("salary_max") else None,
        "url":              raw.get("redirect_url"),
        "description":      raw.get("description"),
        "description_hash": _desc_hash(raw.get("description", "")),
        "source":           "adzuna",
        "status":           "new_leads",
    }


def _passes_hard_filters(job: Job, profile) -> tuple[bool, str]:
    """
    Hard filters run before scoring — immediate disqualifiers.
    Returns (passes, reason_if_rejected).
    """
    text = f"{job.title or ''} {job.description or ''}".lower()

    for word in (profile.exclusion_words or []):
        if word.lower() in text:
            return False, f'exclusion keyword: "{word}"'

    # Only reject on salary if the listing actually states a max
    if profile.salary_floor and job.salary_max:
        if job.salary_max < profile.salary_floor:
            return False, f"salary max ${job.salary_max:,} below floor ${profile.salary_floor:,}"

    return True, ""


async def run_ingest(config: dict, db: Session) -> dict:
    """
    Pull jobs from Adzuna, deduplicate, hard-filter, score, and save.
    config keys: keywords, country, location, max_pages, results_per_page
    Returns a summary of what happened.
    """
    profile = db.query(Profile).first()

    keywords         = config.get("keywords", "")
    country          = config.get("country", "us")
    location         = config.get("location", "")
    max_pages        = int(config.get("max_pages", 2))
    results_per_page = int(config.get("results_per_page", 50))

    summary = {"fetched": 0, "skipped_dedup": 0, "skipped_filter": 0, "saved": 0}

    for page in range(1, max_pages + 1):
        raw_results = await search_jobs(
            keywords=keywords,
            country=country,
            location=location,
            page=page,
            results_per_page=results_per_page,
        )

        if not raw_results:
            break  # Adzuna returned nothing — no more pages

        summary["fetched"] += len(raw_results)

        for raw in raw_results:
            job_data = _map_adzuna(raw)

            # ── Dedup by adzuna_id ────────────────────────────────────────────
            if db.query(Job).filter(Job.adzuna_id == job_data["adzuna_id"]).first():
                summary["skipped_dedup"] += 1
                continue

            job = Job(**job_data)

            # ── Hard filters ──────────────────────────────────────────────────
            if profile:
                passes, _ = _passes_hard_filters(job, profile)
                if not passes:
                    summary["skipped_filter"] += 1
                    continue

            # ── Scoring pipeline (same two-tier logic as manual create) ───────
            if profile:
                score, reasons = compute_fit(job, profile)
                if score >= 40 and settings.anthropic_api_key:
                    score, reasons = await compute_fit_ai(job, profile)
                job.fit_score = score
                job.fit_reasons = reasons

            db.add(job)
            summary["saved"] += 1

        db.commit()

        # Polite pause between pages to respect Adzuna rate limits
        if page < max_pages:
            await asyncio.sleep(0.5)

    return summary