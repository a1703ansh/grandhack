from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health(seed_path):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["topics"] >= 10


def test_roadmap_api_demo_query(seed_path):
    resp = client.post(
        "/api/roadmap",
        json={
            "goal": "master deep learning",
            "currentKnowledge": "python basics",
            "weeksAvailable": 12,
            "weeklyHours": 15,
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["goal"] == "Deep Learning"
    assert len(body["stages"]) >= 6
    assert body["graph"]["nodes"]
    assert "stages" in body and "graph" in body


def test_roadmap_api_unknown_goal(seed_path):
    resp = client.post(
        "/api/roadmap",
        json={"goal": "pyrotechnics", "weeklyHours": 10},
    )
    assert resp.status_code == 404


def test_topics_endpoint(seed_path):
    resp = client.get("/api/topics")
    assert resp.status_code == 200
    assert any(t["id"] == "deep_learning" for t in resp.json())


def test_courses_endpoint(seed_path):
    resp = client.get("/api/courses?topic=linear%20algebra&limit=3")
    assert resp.status_code == 200
    courses = resp.json()
    assert 2 <= len(courses) <= 3
    assert all(c["source"] in {"MIT OCW", "Khan Academy", "NPTEL", "Coursera Audit", "YouTube"} for c in courses)


def test_graph_subtree(seed_path):
    resp = client.get("/api/graph/deep%20learning")
    assert resp.status_code == 200
    body = resp.json()
    assert body["topic"] == "deep_learning"
    assert len(body["order"]) >= 6


def test_export_roundtrip(seed_path):
    rid = client.post(
        "/api/roadmap",
        json={"goal": "deep learning", "currentKnowledge": "python basics", "weeklyHours": 12},
    ).json()["id"]
    md = client.get(f"/api/export/{rid}?format=markdown")
    assert md.status_code == 200
    assert md.headers["content-type"].startswith("text/markdown")
    assert "Weekly Plan" in md.text

    ics = client.get(f"/api/export/{rid}?format=ics")
    assert ics.status_code == 200
    assert ics.headers["content-type"].startswith("text/calendar")
    assert ics.text.startswith("BEGIN:VCALENDAR")