import re
from typing import List, Tuple

import anthropic

from ..config import settings


# ── Rule-based scorer ─────────────────────────────────────────────────────────

def _word_match(term: str, text: str) -> bool:
    """True if `term` appears as a whole word in `text` (case-insensitive)."""
    return bool(re.search(rf"\b{re.escape(term)}\b", text))


def compute_fit(job, profile) -> Tuple[int, List[dict]]:
    """
    Fast rule-based fit score. Starts at 50 (neutral), adds/subtracts per
    signal, clamps to 0-100. Used as a first-pass filter before AI scoring.
    """
    score = 50
    reasons = []

    text = f"{job.title or ''} {job.description or ''}".lower()
    title_lower = (job.title or "").lower()

    # ── Title match (+20 per match, capped at +30) ────────────────────────────
    target_titles = profile.target_titles or []
    matched_titles = [t for t in target_titles if t.lower() in title_lower]
    if matched_titles:
        score += min(30, len(matched_titles) * 20)
        reasons.append({"type": "pro", "text": f"Title matches your target: {', '.join(matched_titles)}"})
    elif target_titles:
        reasons.append({"type": "con", "text": "Title doesn't match any of your target roles"})

    # ── Skills match (+25 max, proportional) ─────────────────────────────────
    # profile.skills is JSONB → list of dicts from SQLAlchemy
    raw_skills = profile.skills or []
    user_skill_names = [
        (s["name"] if isinstance(s, dict) else s.name).lower()
        for s in raw_skills
    ]
    # Word-boundary match prevents "ml" hitting "yaml", "sql" hitting "nosql", etc.
    matched_skills = [s for s in user_skill_names if _word_match(s, text)]
    if user_skill_names:
        pct = len(matched_skills) / len(user_skill_names)
        score += round(pct * 25)
        if matched_skills:
            display = ", ".join(matched_skills[:5])
            suffix = f" (+{len(matched_skills) - 5} more)" if len(matched_skills) > 5 else ""
            reasons.append({"type": "pro", "text": f"Mentions {len(matched_skills)}/{len(user_skill_names)} of your skills: {display}{suffix}"})
        else:
            reasons.append({"type": "con", "text": "None of your skills appear in this posting"})

    # ── Salary floor (+10 if met, −20 if max is below floor) ─────────────────
    if profile.salary_floor:
        if job.salary_min and job.salary_min >= profile.salary_floor:
            score += 10
            reasons.append({"type": "pro", "text": f"Salary range meets your floor (min ${job.salary_min:,})"})
        elif job.salary_max and job.salary_max < profile.salary_floor:
            score -= 20
            reasons.append({"type": "con", "text": f"Max salary ${job.salary_max:,} is below your floor of ${profile.salary_floor:,}"})

    # ── Exclusion words (−10 each) ────────────────────────────────────────────
    for word in (profile.exclusion_words or []):
        if word.lower() in text:
            score -= 10
            reasons.append({"type": "con", "text": f'Contains exclusion keyword: "{word}"'})

    # ── Remote preference (±10) ───────────────────────────────────────────────
    pref = profile.remote_pref
    if pref and pref != "any":
        loc = (job.location or "").lower()
        is_remote = "remote" in loc or "remote" in text
        if pref == "remote" and is_remote:
            score += 10
            reasons.append({"type": "pro", "text": "Remote position matches your preference"})
        elif pref == "remote" and not is_remote:
            score -= 10
            reasons.append({"type": "con", "text": "Position doesn't appear to be remote"})
        elif pref == "onsite" and not is_remote:
            score += 5
            reasons.append({"type": "pro", "text": "On-site position matches your preference"})

    return max(0, min(100, score)), reasons


# ── AI scorer (runs only when rule-based score >= 40) ─────────────────────────

_SCORE_TOOL = {
    "name": "score_job_fit",
    "description": "Score how well a job posting matches a candidate's profile.",
    "input_schema": {
        "type": "object",
        "properties": {
            "fit_score": {
                "type": "integer",
                "description": "Overall fit score from 0 to 100",
            },
            "fit_reasons": {
                "type": "array",
                "description": "Key pros and cons explaining the score",
                "items": {
                    "type": "object",
                    "properties": {
                        "type": {"type": "string", "enum": ["pro", "con"]},
                        "text": {"type": "string"},
                    },
                    "required": ["type", "text"],
                },
            },
        },
        "required": ["fit_score", "fit_reasons"],
    },
}


async def compute_fit_ai(job, profile) -> Tuple[int, List[dict]]:
    """
    Semantic AI scoring via Claude. Called only when rule-based score >= 40.
    Understands synonyms, abbreviations, and adjacent roles.
    """
    skills_text = ", ".join(
        f"{s['name'] if isinstance(s, dict) else s.name} ({s['level'] if isinstance(s, dict) else s.level})"
        for s in (profile.skills or [])
    ) or "none listed"

    titles_text  = ", ".join(profile.target_titles or [])  or "none listed"
    excl_text    = ", ".join(profile.exclusion_words or []) or "none"
    salary_floor = f"${profile.salary_floor:,}" if profile.salary_floor else "not set"

    if job.salary_min and job.salary_max:
        salary_range = f"${job.salary_min:,} – ${job.salary_max:,}"
    elif job.salary_min:
        salary_range = f"from ${job.salary_min:,}"
    elif job.salary_max:
        salary_range = f"up to ${job.salary_max:,}"
    else:
        salary_range = "not listed"

    prompt = f"""Score this job posting against the candidate's profile.

CANDIDATE PROFILE:
- Target titles: {titles_text}
- Skills: {skills_text}
- Remote preference: {profile.remote_pref or 'any'}
- Salary floor: {salary_floor}
- Exclusion keywords: {excl_text}

JOB POSTING:
- Title: {job.title or 'Unknown'}
- Company: {job.company or 'Unknown'}
- Location: {job.location or 'Not listed'}
- Salary: {salary_range}
- Description: {(job.description or '')[:3000]}

Use semantic understanding — recognise abbreviations (ML = machine learning, PG = PostgreSQL), \
synonyms (pipelines ≈ ETL), and adjacent roles. Return a fit_score (0-100) and concise pros/cons."""

    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
    response = await client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=512,
        tools=[_SCORE_TOOL],
        tool_choice={"type": "tool", "name": "score_job_fit"},
        messages=[{"role": "user", "content": prompt}],
    )

    for block in response.content:
        if block.type == "tool_use" and block.name == "score_job_fit":
            data = block.input
            score = max(0, min(100, int(data.get("fit_score", 50))))
            return score, data.get("fit_reasons", [])

    return 50, []