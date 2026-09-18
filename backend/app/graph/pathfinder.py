"""Personalized pathfinding over the prerequisite graph.

core idea: walk backward from the goal to collect its prerequisite closure,
drop topics the learner already knows, order the remainder topologically,
then allocate the time budget across stages proportionally to effort hours.
"""

from __future__ import annotations

import math

from .graph import KnowledgeGraph


class NoTopicMatchError(Exception):
    pass


def closure(graph: KnowledgeGraph, goal: str, satisfied: set[str] | None = None) -> list[str]:
    """Topologically-ordered prerequisite chain from goal backwards.

    Includes the goal itself, excludes satisfied topics (and their ancestors,
    which are implicitly known). Raises NoTopicMatchError when goal is unknown.
    """
    satisfied = satisfied or set()
    if goal not in graph.topics:
        raise NoTopicMatchError(goal)

    # ---- backward walk: collect every ancestor of the goal
    needed: set[str] = set()
    stack = [goal]
    while stack:
        node = stack.pop()
        for parent in graph.reverse.get(node, ()):
            if parent not in needed:
                needed.add(parent)
                stack.append(parent)

    curriculum = {goal} | needed

    # ---- drop topics the learner already knows (and their ancestors,
    #      which are implicitly known too), but never drop the goal itself
    removed: set[str] = set()
    stack = list(satisfied & curriculum)
    while stack:
        node = stack.pop()
        if node in removed:
            continue
        removed.add(node)
        for parent in graph.reverse.get(node, ()):
            if parent in curriculum:
                stack.append(parent)
    curriculum -= removed
    curriculum.add(goal)

    # ---- topological order restricted to the curriculum
    indegree = {tid: 0 for tid in curriculum}
    for e in graph.edges:
        if e["from"] in curriculum and e["to"] in curriculum:
            indegree[e["from"]] += 0
            indegree[e["to"]] += 1

    ready = [tid for tid in curriculum if indegree[tid] == 0]
    ready.sort(key=lambda t: -_depth_penalty(graph, t))
    order: list[str] = []
    while ready:
        node = ready.pop(0)
        order.append(node)
        for nxt in sorted(graph.adj.get(node, ())):
            if nxt not in curriculum:
                continue
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                ready.append(nxt)
                # keep 'ready' deterministic
                ready.sort(key=lambda t: -_depth_penalty(graph, t))
    if len(order) != len(curriculum):
        raise RuntimeError(f"cycle or trailing nodes in curriculum {curriculum - set(order)}")
    return order


def _depth_penalty(graph: KnowledgeGraph, topic_id: str) -> int:
    return graph.goal_id_order.index(topic_id) if topic_id in graph.goal_id_order else 0


def prereqs_within(graph: KnowledgeGraph, topic_id: str, curriculum: list[str]) -> list[str]:
    """Direct prerequisites of a curriculum topic, filtered to the curriculum."""
    cset = set(curriculum)
    out = sorted(set(graph.reverse.get(topic_id) or ()) & cset, key=curriculum.index)
    return out


def allocate_weeks(ordered_hours: list[float], weekly_hours: float) -> list[tuple[int, int]]:
    """Spread cumulative effort across calendar weeks.

    Returns (weekStart, weekEnd) per stage (1-indexed). Stages are laid out
    back-to-back; totalWeeks = ceil(total_hours / weekly_hours).
    """
    if not ordered_hours:
        return []
    total = sum(ordered_hours)
    weeks = max(1, math.ceil(total / max(weekly_hours, 1e-6)))
    acc = 0.0
    segments: list[tuple[int, int]] = []
    for h in ordered_hours:
        start = int(acc / max(weekly_hours, 1e-6)) + 1
        acc += h
        end = int((acc - 1e-9) / max(weekly_hours, 1e-6)) + 1
        end = max(start, end)
        segments.append((min(start, weeks), min(end, weeks)))
    return segments