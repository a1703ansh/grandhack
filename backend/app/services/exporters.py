"""Deterministic roadmap exports: Notion-ready Markdown + .ics calendar feed."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from app.schemas import Roadmap, RoadmapStage

_DIFF_BADGE = {"Beginner": "[Beginner]", "Intermediate": "[Intermediate]", "Advanced": "[Advanced]"}


def to_markdown(roadmap: Roadmap) -> str:
    lines: list[str] = []
    lines.append(f"# Your {roadmap.goal} Roadmap")
    lines.append("")
    lines.append(f"- **Duration:** {roadmap.totalWeeks} weeks")
    lines.append(f"- **Total effort:** {roadmap.totalHours:.0f} hours")
    lines.append(f"- **Sources:** 100% free (MIT OCW, Khan Academy, NPTEL, Coursera audit, YouTube)")
    lines.append("")
    lines.append("## Weekly Plan")
    lines.append("")
    for i, stage in enumerate(roadmap.stages, start=1):
        lines.append(f"### {i}. {stage.title}")
        lines.append("")
        lines.append(
            f"- **Weeks:** {stage.weekStart}"
            + ("" if stage.weekStart == stage.weekEnd else f"–{stage.weekEnd}")
            + f" · **Effort:** {stage.estimatedHours:.0f}h · {_DIFF_BADGE[stage.difficulty]}"
        )
        if stage.prerequisites:
            lines.append(f"- **Requires:** {', '.join(stage.prerequisites)}")
        lines.append("")
        lines.append(stage.description)
        lines.append("")
        lines.append(f"**Why this comes next:** {stage.whyNext}")
        lines.append("")
        if stage.recommendedCourses:
            lines.append("Recommended free courses:")
            lines.append("")
            for c in stage.recommendedCourses:
                lines.append(
                    f"- [{c.title}]({c.url}) — {c.source}, ~{c.durationHours:.0f}h, "
                    f"rated {c.rating:.1f}/5"
                )
            lines.append("")
    return "\n".join(lines) + "\n"


def to_ics(roadmap: Roadmap) -> str:
    events: list[str] = ["BEGIN:VCALENDAR", "VERSION:2.0",
                        "PRODID:-//CredentialFree Learning Path Finder//EN",
                        "CALSCALE:GREGORIAN", "METHOD:PUBLISH"]
    today = datetime.combine(date.today(), datetime.min.time())
    # schedule starts next Monday
    start = today + timedelta(days=(7 - today.weekday()) % 7)

    def stage_dates(stage: RoadmapStage) -> tuple[date, date]:
        begin = (start + timedelta(weeks=stage.weekStart - 1)).date()
        end = (start + timedelta(weeks=stage.weekEnd)).date()
        return begin, end

    for idx, stage in enumerate(roadmap.stages, start=1):
        begin, end = stage_dates(stage)
        course_names = "; ".join(c.title for c in stage.recommendedCourses)
        description = (
            f"{stage.description}\n\nWhy: {stage.whyNext}\n\n"
            f"Courses: {course_names}"
        ).replace("\n", "\\n")
        events.extend(
            [
                "BEGIN:VEVENT",
                f"UID:{roadmap.id}-{idx}@credential-free-path",
                f"DTSTAMP:{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
                f"DTSTART;VALUE=DATE:{begin.strftime('%Y%m%d')}",
                f"DTEND;VALUE=DATE:{end.strftime('%Y%m%d')}",
                f"SUMMARY:{stage.title} ({stage.estimatedHours:.0f}h)",
                f"DESCRIPTION:{description}",
                "END:VEVENT",
            ]
        )
    events.append("END:VCALENDAR")
    return "\r\n".join(events) + "\r\n"