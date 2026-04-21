from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import ingest, jobs, parse, profile
from .models import ingest_config, job, profile as profile_model  # noqa: F401 — registers models with Base.metadata

app = FastAPI(title="Job-Flow API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(jobs.router)
app.include_router(parse.router)
app.include_router(profile.router)
app.include_router(ingest.router)


@app.get("/health")
async def health():
    return {"status": "ok"}