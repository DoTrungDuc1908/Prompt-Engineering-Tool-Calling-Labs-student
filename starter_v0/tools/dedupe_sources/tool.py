from __future__ import annotations

import re
from collections import defaultdict
from typing import Any

from tools._shared import fold_text
from tools.source_audit.tool import normalize_url


VALID_STRATEGIES = {"url_then_title", "url_only", "title_only"}


def _title_key(item: dict[str, Any]) -> str:
    folded = fold_text(str(item.get("title") or ""))
    return re.sub(r"[^a-z0-9]+", " ", folded).strip()


def _key_for(item: dict[str, Any], strategy: str, index: int) -> str:
    url_key = normalize_url(str(item.get("url") or ""))
    title_key = _title_key(item)
    if strategy == "url_only":
        key = f"url:{url_key}" if url_key else ""
    elif strategy == "title_only":
        key = f"title:{title_key}" if title_key else ""
    else:
        key = f"url:{url_key}" if url_key else (f"title:{title_key}" if title_key else "")
    return key or f"unique:{index}"


def dedupe_sources(items: list[dict[str, Any]] | None = None, strategy: str = "url_then_title") -> dict[str, Any]:
    selected_strategy = strategy if strategy in VALID_STRATEGIES else "url_then_title"
    source_items = [dict(item) for item in (items or [])]
    groups: dict[str, list[int]] = defaultdict(list)
    unique_items: list[dict[str, Any]] = []

    for index, item in enumerate(source_items):
        key = _key_for(item, selected_strategy, index)
        if not groups[key]:
            unique_items.append(item)
        groups[key].append(index)

    duplicate_groups = [
        {"key": key, "kept_index": indexes[0], "duplicate_indexes": indexes[1:]}
        for key, indexes in groups.items()
        if len(indexes) > 1
    ]
    return {
        "tool": "dedupe_sources",
        "strategy": selected_strategy,
        "items": unique_items,
        "duplicate_groups": duplicate_groups,
        "summary": {
            "input_count": len(source_items),
            "unique_count": len(unique_items),
            "removed_count": len(source_items) - len(unique_items),
        },
    }
