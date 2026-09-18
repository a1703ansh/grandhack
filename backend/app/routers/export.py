"""GET /api/export/{id}?format=markdown|ics""" 

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response

from app.services import roadmap_service
from app.services.exporters import to_ics, to_markdown

router = APIRouter(prefix="/export", tags=["export"])

_CONTENT_TYPE = {"markdown": "text/markdown; charset=utf-8", "ics": "text/calendar; charset=utf-8"}
_EXT = {"markdown": "md", "ics": "ics"}


@router.get("/{rid}")
async def export_roadmap(
    rid: str,
    format: str = Query("markdown", pattern="^(markdown|ics)$"),
) -> Response:
    roadmap = roadmap_service.get_roadmap(rid)
    if not roadmap:
        raise HTTPException(status_code=404, detail=f"Roadmap '{rid}' not found or expired.")
    content = to_markdown(roadmap) if format == "markdown" else to_ics(roadmap)
    filename = f"{roadmap.id}.{_EXT[format]}"
    return Response(
        content=content,
        media_type=_CONTENT_TYPE[format],
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-store",
        },
    )