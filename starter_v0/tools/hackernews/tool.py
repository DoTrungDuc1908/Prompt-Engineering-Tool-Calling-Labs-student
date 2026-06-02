from __future__ import annotations

from typing import Any

import requests

from tools._shared import err


def top_hn_stories(max_results: int = 5) -> dict[str, Any]:
    try:
        ids_resp = requests.get("https://hacker-news.firebaseio.com/v0/topstories.json", timeout=15)
        ids_resp.raise_for_status()
        ids = ids_resp.json()[:max_results]
        items = []
        for item_id in ids:
            item_resp = requests.get(f"https://hacker-news.firebaseio.com/v0/item/{item_id}.json", timeout=15)
            item_resp.raise_for_status()
            data = item_resp.json()
            if data:
                items.append({
                    "title": data.get("title", ""),
                    "url": data.get("url") or f"https://news.ycombinator.com/item?id={item_id}",
                    "source": "hackernews",
                    "points": data.get("score", 0),
                    "author": data.get("by", ""),
                    "comments": data.get("descendants", 0),
                })
        return {"tool": "top_hn_stories", "items": items}
    except Exception as exc:
        return err("top_hn_stories", exc)
