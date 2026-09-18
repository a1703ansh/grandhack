"""Pydantic schemas. Mirrors frontend/src/types/index.ts exactly so the
API contract on both sides stays in sync by construction."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

Difficulty = Literal["Beginner", "Intermediate", "Advanced"]
CourseSource = Literal["MIT OCW", "Khan Academy", "NPTEL", "Coursera Audit", "YouTube"]


class Course(BaseModel):
    id: str
    title: str
    source: CourseSource
    difficulty: Difficulty
    durationHours: float
    rating: float
    url: str
    tags: list[str]


class RoadmapStage(BaseModel):
    id: str
    weekStart: int
    weekEnd: int
    title: str
    description: str
    difficulty: Difficulty
    estimatedHours: float
    whyNext: str
    prerequisites: list[str]
    recommendedCourses: list[Course] = Field(default_factory=list)


class GraphNode(BaseModel):
    id: str
    label: str
    difficulty: Difficulty
    completed: bool | None = None


class GraphEdge(BaseModel):
    source: str
    target: str


class GraphData(BaseModel):
    nodes: list[GraphNode]
    links: list[GraphEdge]


class Roadmap(BaseModel):
    id: str
    goal: str
    totalWeeks: int
    totalHours: float
    stages: list[RoadmapStage]
    graph: GraphData


class RoadmapRequest(BaseModel):
    goal: str
    currentKnowledge: str = ""
    weeksAvailable: int = Field(default=12, ge=1, le=104)
    weeklyHours: float = Field(default=10, ge=1, le=168)


class ExportRequest(BaseModel):
    format: Literal["markdown", "ics"] = "markdown"