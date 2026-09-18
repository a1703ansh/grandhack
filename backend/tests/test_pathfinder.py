import math

import pytest

from app.graph.graph import KnowledgeGraph
from app.graph.pathfinder import NoTopicMatchError, allocate_weeks, closure, prereqs_within


def test_resolve_goal_variants(graph: KnowledgeGraph):
    assert graph.resolve_topic("master deep learning") == "deep_learning"
    assert graph.resolve_topic("Deep Learning") == "deep_learning"
    assert graph.resolve_topic("I want to learn ML") == "machine_learning_fundamentals"
    assert graph.resolve_topic("data analytics") == "data_science"
    assert graph.resolve_topic("completely unknown thing") in (None, "python_core")
    assert graph.resolve_topic("") is None


def test_resolve_goes_to_advanced_goal_first(graph: KnowledgeGraph):
    # "cnn" is a CV alias, not the python_core collision
    assert graph.resolve_topic("cnn") == "deep_learning_cv"


def test_satisfied_topics(graph: KnowledgeGraph):
    got = graph.satisfied_topics("I know numpy and some calculus")
    assert got == {"python_data_tools", "calculus"}
    assert graph.satisfied_topics("") == set()
    assert graph.satisfied_topics("python basics, linear algebra") == {
        "python_core",
        "linear_algebra",
    }


def test_dl_closure_is_ordered_dag(graph: KnowledgeGraph):
    order = closure(graph, "deep_learning", satisfied=set())
    assert order[0] == "python_core"
    assert order[-1] == "deep_learning"
    assert set(order) == {
        "python_core",
        "python_data_tools",
        "linear_algebra",
        "calculus",
        "probability_stats",
        "machine_learning_fundamentals",
        "neural_networks",
        "deep_learning",
    }
    # topological invariant: every prereq appears before its dependent
    position = {tid: i for i, tid in enumerate(order)}
    for e in graph.edges:
        if e["from"] in position and e["to"] in position:
            assert position[e["from"]] < position[e["to"]], e


def test_closure_skips_known_topics(graph: KnowledgeGraph):
    order = closure(graph, "deep_learning", satisfied={"python_core"})
    assert "python_core" not in order
    assert order[0] == "python_data_tools"
    assert "machine_learning_fundamentals" in order
    # python_core's ancestors can't ghost back in
    assert order[-1] == "deep_learning"


def test_prereqs_within(graph: KnowledgeGraph):
    order = closure(graph, "deep_learning", set())
    prereqs = prereqs_within(graph, "machine_learning_fundamentals", order)
    assert set(prereqs) == {"python_data_tools", "linear_algebra", "probability_stats"}
    # every prereq must come strictly before the dependent
    ml_pos = order.index("machine_learning_fundamentals")
    for p in prereqs:
        assert order.index(p) < ml_pos
    assert prereqs_within(graph, "python_core", order) == []


def test_unknown_goal_raises(graph: KnowledgeGraph):
    with pytest.raises(NoTopicMatchError):
        closure(graph, "pyrotechnics", set())


def test_allocate_weeks_matches_budget(graph: KnowledgeGraph):
    hours = [float(graph.topics[t]["hours"]) for t in
             closure(graph, "deep_learning", set())]
    weekly = 10.0
    total = sum(hours)
    weeks = allocate_weeks(hours, weekly)
    assert len(weeks) == len(hours)
    assert weeks[-1][1] == math.ceil(total / weekly)
    starts = [s for s, _ in weeks]
    assert starts == sorted(starts)
    assert starts[0] == 1
    for (s, e) in weeks:
        assert 1 <= s <= e


def test_allocate_weeks_big_weekly_budget(graph: KnowledgeGraph):
    hours = [10, 20, 5]
    weeks = allocate_weeks(hours, 40)
    assert len(weeks) == 3
    assert weeks[-1][1] == 1  # total 35h fits inside a single 40h week