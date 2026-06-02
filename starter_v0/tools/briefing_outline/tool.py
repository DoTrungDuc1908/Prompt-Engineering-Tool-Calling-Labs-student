from __future__ import annotations

from typing import Any

from tools._shared import domain


AUDIENCE_SECTIONS = {
    "executive": ["Executive summary", "Business impact", "Risks", "Recommended next steps", "Evidence"],
    "technical": ["Problem", "Methods and systems", "Evidence", "Limitations", "Implementation notes"],
    "general": ["Summary", "Key points", "Risks and open questions", "Evidence"],
}


def _evidence_line(index: int, item: dict[str, Any]) -> str:
    title = str(item.get("title") or f"Source {index}").strip()
    url = str(item.get("url") or "").strip()
    source = str(item.get("source") or domain(url) or "missing source").strip()
    return f"- [{index}] {title} - [{source}]({url})" if url else f"- [{index}] {title} - {source}"


def build_briefing_outline(
    items: list[dict[str, Any]] | None = None,
    audience: str = "executive",
    title: str = "Research briefing",
) -> dict[str, Any]:
    source_items = [dict(item) for item in (items or [])]
    selected_audience = audience if audience in AUDIENCE_SECTIONS else "executive"
    sections = AUDIENCE_SECTIONS[selected_audience]
    missing_source_indexes = [
        index
        for index, item in enumerate(source_items, start=1)
        if not str(item.get("url") or "").strip()
    ]

    parts = [f"# {title or 'Research briefing'}", "", f"Audience: {selected_audience}", ""]
    for section in sections:
        parts.append(f"## {section}")
        if section == "Evidence":
            parts.extend(_evidence_line(index, item) for index, item in enumerate(source_items, start=1))
            if not source_items:
                parts.append("- No evidence items supplied.")
        else:
            parts.append("- Add evidence-backed points here.")
        parts.append("")
    if missing_source_indexes:
        parts += [
            "## Source gaps",
            f"- Missing URL for evidence item(s): {', '.join(str(index) for index in missing_source_indexes)}.",
            "",
        ]
    return {
        "tool": "briefing_outline",
        "audience": selected_audience,
        "sections": sections,
        "markdown": "\n".join(parts).strip(),
        "summary": {
            "item_count": len(source_items),
            "missing_source_count": len(missing_source_indexes),
        },
    }
