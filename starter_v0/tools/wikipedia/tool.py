from __future__ import annotations

from typing import Any

import requests

from tools._shared import err


def search_wikipedia(query: str = "", max_results: int = 5) -> dict[str, Any]:
    try:
        search = requests.get(
            "https://en.wikipedia.org/w/api.php",
            params={
                "action": "query",
                "format": "json",
                "list": "search",
                "srsearch": query,
                "srlimit": max_results,
                "srprop": "snippet",
            },
            headers={"User-Agent": "AI20k-Research-Agent/1.0 (educational lab)"},
            timeout=15,
        )
        search.raise_for_status()
        pages = search.json().get("query", {}).get("search", [])
        items = []
        for p in pages:
            items.append({
                "title": p["title"],
                "url": f"https://en.wikipedia.org/wiki/{p['title'].replace(' ', '_')}",
                "source": "wikipedia",
                "summary": p.get("snippet", "").replace("<span class=\"searchmatch\">", "").replace("</span>", ""),
            })
        return {"tool": "search_wikipedia", "query": query, "items": items}
    except Exception as exc:
        return err("search_wikipedia", exc)
