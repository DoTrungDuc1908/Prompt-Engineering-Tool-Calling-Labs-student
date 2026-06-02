from __future__ import annotations

import re
from typing import Any
from urllib.parse import urlsplit

from tools.source_audit.tool import normalize_url


URL_PATTERN = re.compile(r"https?://[^\s<>\"]+")
ARXIV_ID_PATTERN = re.compile(r"(?<![\d.])(\d{4}\.\d{4,5}(?:v\d+)?)(?!\d)")
TRAILING_PUNCTUATION = ".,;:!?)]}'"


def _url_citations(text: str) -> list[dict[str, str]]:
    citations: list[dict[str, str]] = []
    seen: set[str] = set()
    for match in URL_PATTERN.findall(text):
        normalized = normalize_url(match.rstrip(TRAILING_PUNCTUATION))
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        citations.append({
            "kind": "url",
            "value": normalized,
            "url": normalized,
            "domain": urlsplit(normalized).hostname or "",
        })
    return citations


def extract_citations(text: str = "") -> dict[str, Any]:
    citations = _url_citations(text or "")
    covered_text = " ".join(item["url"] for item in citations)
    seen_arxiv_ids = set(ARXIV_ID_PATTERN.findall(covered_text))
    for arxiv_id in ARXIV_ID_PATTERN.findall(text or ""):
        if arxiv_id in seen_arxiv_ids:
            continue
        seen_arxiv_ids.add(arxiv_id)
        citations.append({
            "kind": "arxiv_id",
            "value": arxiv_id,
            "url": f"https://arxiv.org/abs/{arxiv_id}",
            "domain": "arxiv.org",
        })
    return {
        "tool": "extract_citations",
        "citations": citations,
        "summary": {
            "total": len(citations),
            "urls": sum(item["kind"] == "url" for item in citations),
            "standalone_arxiv_ids": sum(item["kind"] == "arxiv_id" for item in citations),
        },
    }
