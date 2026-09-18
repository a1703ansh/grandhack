"""POST /api/roadmap — the flagship endpoint."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.graph.pathfinder import NoTopicMatchError
from app.schemas import Roadmap, RoadmapRequest
from app.services import roadmap_service

router = APIRouter(prefix="/roadmap", tags=["roadmap"])


@router.post("", response_model=Roadmap)
async def create_roadmap(req: RoadmapRequest) -> Roadmap:
    try:
        return await roadmap_service.build_roadmap(req)
    except NoTopicMatchError as exc:
        raise HTTPException(
            status_code=404,
            detail=f"Couldn't map that goal to a topic we cover yet: '{exc}'",
        ) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc