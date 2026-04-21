import httpx

from ..config import settings

ADZUNA_BASE = "https://api.adzuna.com/v1/api/jobs"


async def search_jobs(
    keywords: str,
    country: str = "us",
    location: str = "",
    page: int = 1,
    results_per_page: int = 50,
) -> list[dict]:
    """Fetch one page of jobs from the Adzuna API. Returns raw result list."""
    params = {
        "app_id": settings.adzuna_app_id,
        "app_key": settings.adzuna_app_key,
        "what": keywords,
        "results_per_page": results_per_page,
        "content-type": "application/json",
    }
    if location:
        params["where"] = location

    url = f"{ADZUNA_BASE}/{country}/search/{page}"

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        return resp.json().get("results", [])