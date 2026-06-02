from __future__ import annotations

from collections import Counter
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


SOCIAL_DOMAINS = {"twitter.com", "x.com"}
TRACKING_QUERY_KEYS = {"fbclid", "gclid"}
TRACKING_QUERY_PREFIXES = ("utm_",)


def _host_matches(host: str, domain: str) -> bool:
    return host == domain or host.endswith(f".{domain}")


def _is_tracking_key(key: str) -> bool:
    folded = key.lower()
    return folded in TRACKING_QUERY_KEYS or folded.startswith(TRACKING_QUERY_PREFIXES)


def normalize_url(value: str) -> str:
    raw = (value or "").strip()
    try:
        parsed = urlsplit(raw)
    except ValueError:
        return ""

    scheme = parsed.scheme.lower()
    if scheme not in {"http", "https"} or not parsed.hostname:
        return ""
    if parsed.username or parsed.password:
        return ""

    host = parsed.hostname.lower()
    try:
        port = parsed.port
    except ValueError:
        return ""
    if port and not ((scheme == "http" and port == 80) or (scheme == "https" and port == 443)):
        host = f"{host}:{port}"

    path = parsed.path or "/"
    if path != "/":
        path = path.rstrip("/")
    query = urlencode(
        sorted(
            (key, item)
            for key, item in parse_qsl(parsed.query, keep_blank_values=True)
            if not _is_tracking_key(key)
        ),
        doseq=True,
    )
    return urlunsplit((scheme, host, path, query, ""))


def _category_for(normalized_url: str) -> tuple[str, list[str]]:
    if not normalized_url:
        return "invalid_url", ["invalid_url"]

    host = urlsplit(normalized_url).hostname or ""
    if any(_host_matches(host, domain) for domain in SOCIAL_DOMAINS):
        return "social_signal", ["social_signal_only"]
    if _host_matches(host, "arxiv.org"):
        return "preprint", ["preprint_not_automatically_peer_reviewed"]
    return "web_source", ["source_requires_manual_review"]


def audit_sources(sources: list[str] | str | None = None) -> dict[str, Any]:
    if isinstance(sources, str):
        source_list = [sources]
    else:
        source_list = [str(source) for source in (sources or [])]
    normalized = [normalize_url(source) for source in source_list]
    duplicate_counts = Counter(url for url in normalized if url)
    results: list[dict[str, Any]] = []

    for original, normalized_url in zip(source_list, normalized):
        category, issues = _category_for(normalized_url)
        if normalized_url and duplicate_counts[normalized_url] > 1:
            issues.append("duplicate_url")
        results.append({
            "input": original,
            "normalized_url": normalized_url,
            "domain": urlsplit(normalized_url).hostname or "",
            "category": category,
            "issues": issues,
            "requires_review": True,
        })

    valid_urls = [url for url in normalized if url]
    summary = {
        "total": len(source_list),
        "valid_urls": len(valid_urls),
        "invalid_urls": len(source_list) - len(valid_urls),
        "duplicates": sum(count - 1 for count in duplicate_counts.values() if count > 1),
        "social_signals": sum(item["category"] == "social_signal" for item in results),
        "preprints": sum(item["category"] == "preprint" for item in results),
        "review_required": sum(item["requires_review"] for item in results),
    }
    return {
        "tool": "source_audit",
        "results": results,
        "summary": summary,
        "trust_boundary": (
            "This is a heuristic URL review only. It does not fetch content, "
            "verify factual claims, or establish source credibility."
        ),
    }
