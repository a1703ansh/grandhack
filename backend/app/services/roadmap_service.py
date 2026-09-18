"""Orchestrates the full pipeline: normalize -> closure -> topo -> weeks ->
course ranking -> LLM narrative -> Roadmap response."""

from __future__ import annotations

import hashlib
import json
import logging
import time

from app import config
from app.graph.graph import KnowledgeGraph
from app.graph.pathfinder import (
    NoTopicMatchError,
    allocate_weeks,
    closure,
    prereqs_within,
)
from app.nlp import llm
from app.nlp.ranker import get_ranker
from app.schemas import (
    Course,
    GraphData,
    GraphEdge,
    GraphNode,
    Roadmap,
    RoadmapRequest,
    RoadmapStage,
)

logger = logging.getLogger(__name__)

SEED_MISSING_MSG = (
    "Seed graph not found at {p}. Run `python scripts/build_seed.py` first."
)

_graph: KnowledgeGraph | None = None
_roadmap_cache: dict[str, tuple[float, Roadmap]] = {}


def get_graph() -> KnowledgeGraph:
    global _graph
    if _graph is None:
        if not config.SEED_FILE.exists():
            raise FileNotFoundError(SEED_MISSING_MSG.format(p=config.SEED_FILE))
        _graph = KnowledgeGraph.from_file(config.SEED_FILE)
    return _graph


def roadmap_id(prefs: RoadmapRequest) -> str:
    key = json.dumps(
        {
            "goal": prefs.goal,
            "current": prefs.currentKnowledge,
            "weeks": prefs.weeksAvailable,
            "hours": prefs.weeklyHours,
        },
        sort_keys=True,
    )
    digest = hashlib.sha1(key.encode("utf-8")).hexdigest()[:12]
    return f"rlp_{digest}"


def cache_roadmap(rid: str, roadmap: Roadmap) -> None:
    _roadmap_cache[rid] = (time.time(), roadmap)
    if len(_roadmap_cache) > 64:
        # drop oldest
        for k in sorted(_roadmap_cache, key=lambda k: _roadmap_cache[k][0])[
            : len(_roadmap_cache) - 64
        ]:
            _roadmap_cache.pop(k, None)


def get_roadmap(rid: str) -> Roadmap | None:
    hit = _roadmap_cache.get(rid)
    if not hit:
        return None
    created, roadmap = hit
    if time.time() - created > config.CACHE_TTL_S:
        _roadmap_cache.pop(rid, None)
        return None
    return roadmap


async def build_roadmap(prefs: RoadmapRequest) -> Roadmap:
    graph = get_graph()

    goal = graph.resolve_topic(prefs.goal)
    if not goal:
        raise NoTopicMatchError(prefs.goal)

    satisfied = graph.satisfied_topics(prefs.currentKnowledge)
    order = closure(graph, goal, satisfied)

    hours_map = {t: float(graph.topics[t]["hours"]) for t in order}
    weeks = allocate_weeks([hours_map[t] for t in order], prefs.weeklyHours)

    stages_data = [
        {
            "id": tid,
            "title": graph.topics[tid]["name"],
            "prereqs": prereqs_within(graph, tid, order),
            "next": order[i + 1] if i + 1 < len(order) else None,
            "hours": hours_map[tid],
        }
        for i, tid in enumerate(order)
    ]

    enrich = await llm.enrich_roadmap(
        stages_data, graph.topics[goal]["name"], prefs.currentKnowledge
    )

    ranker = get_ranker(graph)
    stages: list[RoadmapStage] = []
    graph_nodes: list[GraphNode] = []
    graph_links: list[GraphEdge] = []

    for i, sid in enumerate(order):
        topic = graph.topics[sid]
        (week_start, week_end) = weeks[i]
        enrich_entry = enrich.get(sid, {})
        estimated = enrich_entry.get("estimatedHours", topic["hours"])
        why = enrich_entry.get("whyNext") or llm.default_why(graph, sid) or _generic_why(graph, order, i)

        prereq_ids = prereqs_within(graph, sid, order)

        courses = ranker.rank(sid, limit=2)
        course_models = [
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
            for c in courses
        ]

        stages.append(
            RoadmapStage(
                id=sid,
                weekStart=week_start,
                weekEnd=week_end,
                title=topic["name"],
                description=topic["description"],
                difficulty=topic["difficulty"],
                estimatedHours=estimated,
                whyNext=why,
                prerequisites=prereq_ids,
                recommendedCourses=course_models,
            )
        )
        graph_nodes.append(
            GraphNode(id=sid, label=topic["name"], difficulty=topic["difficulty"])
        )

    for e in graph.edges:
        if e["from"] in order and e["to"] in order:
            graph_links.append(GraphEdge(source=e["from"], target=e["to"]))

    total_hours = sum(s.estimatedHours for s in stages)
    result = Roadmap(
        id=roadmap_id(prefs),
        goal=graph.topics[goal]["name"],
        totalWeeks=weeks[-1][1] if weeks else 0,
        totalHours=total_hours,
        stages=stages,
        graph=GraphData(nodes=graph_nodes, links=graph_links),
    )
    cache_roadmap(result.id, result)
    return result


def _generic_why(graph: KnowledgeGraph, order: list[str], index: int) -> str:
    sid = order[index]
    prereq_ids = prereqs_within(graph, sid, order)
    if not prereq_ids:
        return f"Every skill needs a starting point. This is the foundation the rest of this path builds on."
    names = ", ".join(graph.topics[p]["name"] for p in prereq_ids)
    return f"Builds directly on {names}. Master each dependency first — everything further down the path assumes this one."