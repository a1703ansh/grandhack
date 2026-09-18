"""GET /api/graph/{topic} — full prerequisite subtree for visualization."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.graph.pathfinder import closure
from app.schemas import GraphData, GraphEdge, GraphNode
from app.services.roadmap_service import get_graph

router = APIRouter(prefix="/graph", tags=["graph"])


class SubtreeResponse(BaseModel):
    topic: str
    name: str
    order: list[str]
    graph: GraphData


@router.get("/{topic}", response_model=SubtreeResponse)
async def fetch_subtree(topic: str) -> SubtreeResponse:
    graph = get_graph()
    tid = graph.resolve_topic(topic)
    if not tid:
        raise HTTPException(status_code=404, detail=f"Unknown topic: '{topic}'")
    order = closure(graph, tid, satisfied=set())
    nodes = [
        GraphNode(id=x, label=graph.topics[x]["name"], difficulty=graph.topics[x]["difficulty"])
        for x in order
    ]
    links = [
        GraphEdge(source=e["from"], target=e["to"])
        for e in graph.edges
        if e["from"] in order and e["to"] in order
    ]
    return SubtreeResponse(
        topic=tid, name=graph.topics[tid]["name"], order=order, graph=GraphData(nodes=nodes, links=links)
    )