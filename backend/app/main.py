"""FastAPI entrypoint.

Dev: two servers (frontend on :3000, API on :8000) with CORS.
Demo: build the frontend with `output: 'export'`; FastAPI serves the static
build from frontend/out on a single port with SPA fallback for /roadmap.
"""

from __future__ import annotations

import logging
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

from app import config
from app.routers import courses, export, graph, search, topics
from app.services.roadmap_service import get_graph

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="Credential-Free Learning Path Finder",
    description="Syllabus-graph roadmaps over free courses (MIT OCW, Khan, NPTEL, Coursera audit).",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search.router, prefix="/api")
app.include_router(graph.router, prefix="/api")
app.include_router(courses.router, prefix="/api")
app.include_router(export.router, prefix="/api")
app.include_router(topics.router, prefix="/api")


@app.get("/api/health")
async def health() -> dict:
    found = config.SEED_FILE.exists()
    return {
        "status": "ok" if found else "seed-missing",
        "seed": str(config.SEED_FILE),
        "seed_exists": found,
        "gemini_configured": bool(config.GEMINI_API_KEY),
        "topics": len(get_graph().topics) if found else 0,
    }


@app.get("/", include_in_schema=False)
async def index():
    html = config.FRONTEND_DIR / "index.html"
    if html.is_file():
        return FileResponse(html)
    return JSONResponse({"service": "Credential-Free Learning Path Finder", "docs": "/docs"})


@app.get("/{full_path:path}", include_in_schema=False)
async def spa(full_path: str):
    """Serve the static frontend export with SPA fallback (demo single-port)."""
    root: Path = config.FRONTEND_DIR
    if not root.is_dir():
        raise HTTPException(status_code=404, detail="Frontend build not found in frontend/out.")
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404)
    for candidate in (
        root / full_path,
        root / f"{full_path}.html",
        root / full_path / "index.html",
    ):
        if candidate.is_file():
            return FileResponse(candidate)
    return FileResponse(root / "index.html")