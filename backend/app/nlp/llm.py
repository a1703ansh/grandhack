"""Gemini-powered enrichment (the "why this order" narrative + effort hours).

Design constraint: this is the ONLY runtime LLM layer — a single batched call
per roadmap (not 40). When no key is present, the API times out, or the
response is invalid, we degrade to deterministic templates so the demo never
hard-fails offline.
"""

from __future__ import annotations

import json
import logging

import httpx

from app import config

logger = logging.getLogger(__name__)

_SYSTEM_TEXT = (
    "You are the reasoning engine of a credential-free learning path finder. "
    "A learner tells you a goal and their current level; you build the "
    "prerequisite chain. Help them understand WHY the order matters and how "
    "much effort each stage realistically takes, using only free resources."
)

_PROMPT_TEMPLATE = """Learner goal: "{goal}"
Learner starts knowing: "{current}"
Choosen prerequisite chain (already topologically ordered):
{stages}

For every stage return this exact JSON:
{{
  "stages": [
    {{
      "id": "<stage id>",
      "whyNext": "2-3 sentence, human reason why this stage belongs here and "
                 "what it unblocks (reference learner background when relevant)",
      "estimatedHours": <integer hours to complete, realistic for a part-time learner>
    }}
  ]
}}
Return JSON only."""


def default_why(graph, stage_id: str) -> str:
    return graph.topics[stage_id].get("why", "")


async def enrich_roadmap(stages: list[dict], goal: str, current: str) -> dict[str, dict]:
    """One batched Gemini call -> {stage_id: {whyNext, estimatedHours}}."""
    if not config.GEMINI_API_KEY:
        return {}
    stage_block = json.dumps(
        [
            {
                "id": s["id"],
                "title": s["title"],
                "prerequisites": s["prereqs"],
                "hours": s["hours"],
            }
            for s in stages
        ],
        ensure_ascii=False,
        indent=1,
    )
    prompt = _PROMPT_TEMPLATE.format(
        goal=goal, current=current or "(none stated)", stages=stage_block
    )
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "systemInstruction": {"parts": [{"text": _SYSTEM_TEXT}]},
        "generationConfig": {"responseMimeType": "application/json", "temperature": 0.4},
    }
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{config.GEMINI_MODEL}:generateContent"
    )
    headers = {"x-goog-api-key": config.GEMINI_API_KEY, "Content-Type": "application/json"}
    try:
        async with httpx.AsyncClient(timeout=config.GEMINI_TIMEOUT_S) as client:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        parsed = json.loads(text)
        out: dict[str, dict] = {}
        for item in parsed.get("stages", []):
            sid = item.get("id")
            if not sid:
                continue
            entry: dict[str, object] = {}
            why = (item.get("whyNext") or "").strip()
            if 12 <= len(why) <= 600:
                entry["whyNext"] = why
            hours = item.get("estimatedHours")
            if isinstance(hours, (int, float)) and 1 <= hours <= 1000:
                entry["estimatedHours"] = round(float(hours))
            if entry:
                out[sid] = entry
        return out
    except Exception as exc:  # noqa: BLE001 - LLM is optional
        logger.info("Gemini enrichment skipped: %s", exc)
        return {}