from __future__ import annotations

from typing import Any

import requests

from tools._shared import err


def search_hn(query: str = "", max_results: int = 5) -> dict[str, Any]:
    try:
        resp = requests.get(
            "https://hn.algolia.com/api/v1/search",
            params={"query": query, "hitsPerPage": max_results},
            timeout=15,
        )
        resp.raise_for_status()
        hits = resp.json().get("hits", [])
        items = []
        for h in hits:
            items.append({
                "title": h.get("title", ""),
                "url": h.get("url") or f"https://news.ycombinator.com/item?id={h.get('objectID', '')}",
                "source": "hackernews",
                "summary": h.get("story_text", "")[:300] if h.get("story_text") else "",
                "points": h.get("points", 0),
                "author": h.get("author", ""),
            })
        return {"tool": "search_hn", "query": query, "items": items}
    except Exception as exc:
        return err("search_hn", exc)
