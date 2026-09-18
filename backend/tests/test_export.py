import asyncio

from app.schemas import RoadmapRequest
from app.services.exporters import to_ics, to_markdown
from app.services.roadmap_service import build_roadmap


def _request() -> RoadmapRequest:
    return RoadmapRequest(
        goal="master deep learning",
        currentKnowledge="python basics",
        weeksAvailable=12,
        weeklyHours=15,
    )


def test_build_roadmap_end_to_end(seed_path):
    roadmap = asyncio.run(build_roadmap(_request()))
    assert roadmap.goal == "Deep Learning"
    assert len(roadmap.stages) >= 6
    # personalization: user already knows Python basics
    assert "python_core" not in {s.id for s in roadmap.stages}
    assert roadmap.totalHours > 0
    assert roadmap.totalWeeks >= 1

    stage_ids = [s.id for s in roadmap.stages]
    assert [n.id for n in roadmap.graph.nodes] == stage_ids
    for s in roadmap.stages:
        assert set(s.prerequisites) <= set(stage_ids)
        assert s.estimatedHours > 0
        assert s.whyNext
        for c in s.recommendedCourses:
            assert c.rating >= 0 and c.tags and c.url.startswith("http")


def test_markdown_export(seed_path):
    roadmap = asyncio.run(build_roadmap(_request()))
    md = to_markdown(roadmap)
    assert md.startswith(f"# Your {roadmap.goal} Roadmap")
    assert "## Weekly Plan" in md
    for s in roadmap.stages:
        assert s.title in md
    assert "Why this comes next" in md


def test_ics_export(seed_path):
    roadmap = asyncio.run(build_roadmap(_request()))
    ics = to_ics(roadmap)
    assert ics.startswith("BEGIN:VCALENDAR")
    assert ics.count("BEGIN:VEVENT") == len(roadmap.stages)
    assert ics.count("END:VEVENT") == len(roadmap.stages)
    assert "DTSTART;VALUE=DATE:" in ics