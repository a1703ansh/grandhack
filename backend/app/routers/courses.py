"""GET /api/courses?topic=X — ranked free courses for one topic."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app.nlp.ranker import get_ranker
from app.schemas import Course
from app.services.roadmap_service import get_graph

router = APIRouter(prefix="/courses", tags=["courses"])


@router.get("", response_model=list[Course])
async def list_courses(
    topic: str = Query(..., description="Topic name or alias"),
    limit: int = Query(5, ge=1, le=10),
) -> list[Course]:
    graph = get_graph()
    tid = graph.resolve_topic(topic)
    if not tid:
        raise HTTPException(status_code=404, detail=f"Unknown topic: '{topic}'")
    ranker = get_ranker(graph)
    return [
        Course(
            id=c["id"],
            title=c["title"],
            source=c["source"],
            difficulty=c["difficulty"],
            durationHours=c["durationHours"],
            rating=c["rating"],
            url=c["url"],
            tags=c["tags"],
        )
        for c in ranker.rank(tid, limit=limit)
    ]