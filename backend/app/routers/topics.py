"""GET /api/topics — supported topics + aliases (for autocomplete)."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.roadmap_service import get_graph

router = APIRouter(prefix="/topics", tags=["topics"])


class TopicInfo(BaseModel):
    id: str
    name: str
    difficulty: str
    aliases: list[str]


@router.get("", response_model=list[TopicInfo])
async def list_topics() -> list[TopicInfo]:
    graph = get_graph()
    return [
        TopicInfo(
            id=tid,
            name=graph.topics[tid]["name"],
            difficulty=graph.topics[tid]["difficulty"],
            aliases=graph.aliases.get(tid, []),
        )
        for tid in graph.goal_id_order
    ]