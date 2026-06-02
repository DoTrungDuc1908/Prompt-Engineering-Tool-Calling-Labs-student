from __future__ import annotations

from typing import Any
from urllib.parse import urlsplit

from tools.source_audit.tool import SOCIAL_DOMAINS, _host_matches, normalize_url


FORUM_DOMAINS = {"reddit.com", "news.ycombinator.com"}


def _rank(item: dict[str, Any]) -> tuple[int, list[str], bool]:
    normalized_url = normalize_url(str(item.get("url") or ""))
    host = urlsplit(normalized_url).hostname or ""
    source_type = str(item.get("source_type") or "").strip().lower()
    score = 50
    reasons = ["general_web_source"]
    requires_review = True

    if not normalized_url:
        return 0, ["missing_or_invalid_url"], True
    if source_type in {"official", "primary"}:
        score += 25
        reasons.append("declared_primary_or_official")
    if host.endswith(".gov") or host == "gov":
        score += 15
        reasons.append("government_domain")
    if host.endswith(".edu") or host == "edu":
        score += 10
        reasons.append("education_domain")
    if _host_matches(host, "arxiv.org"):
        score = max(score, 65)
        reasons.append("arxiv_preprint_requires_review")
    if any(_host_matches(host, domain) for domain in SOCIAL_DOMAINS):
        score = min(score, 25)
        reasons.append("social_signal_only")
    if any(_host_matches(host, domain) for domain in FORUM_DOMAINS):
        score = min(score, 30)
        reasons.append("forum_signal_only")
    return min(score, 100), reasons, requires_review


def rank_sources(items: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    ranked_items: list[dict[str, Any]] = []
    for index, original in enumerate(items or []):
        item = dict(original)
        score, reasons, requires_review = _rank(item)
        ranked_items.append({
            **item,
            "original_index": index,
            "normalized_url": normalize_url(str(item.get("url") or "")),
            "heuristic_score": score,
            "reasons": reasons,
            "requires_review": requires_review,
        })
    ranked_items.sort(key=lambda item: (-item["heuristic_score"], item["original_index"]))
    return {
        "tool": "rank_sources",
        "items": ranked_items,
        "summary": {
            "total": len(ranked_items),
            "manual_review_required": sum(item["requires_review"] for item in ranked_items),
        },
        "trust_boundary": (
            "Scores are deterministic triage hints only. They do not verify "
            "claims or establish source credibility."
        ),
    }
