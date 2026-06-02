from __future__ import annotations

from typing import Any

import requests

from tools._shared import err


def country_info(country: str = "") -> dict[str, Any]:
    try:
        resp = requests.get(f"https://restcountries.com/v3.1/name/{country}", timeout=15)
        if resp.status_code == 404:
            return {"tool": "country_info", "country": country, "items": []}
        resp.raise_for_status()
        data = resp.json()
        items = []
        for c in data:
            items.append({
                "name": c.get("name", {}).get("common", ""),
                "official_name": c.get("name", {}).get("official", ""),
                "capital": ", ".join(c.get("capital", [])),
                "region": c.get("region", ""),
                "population": c.get("population", 0),
                "area_km2": c.get("area", 0),
                "languages": ", ".join(c.get("languages", {}).values()),
                "currency": ", ".join(f"{k} ({v.get('name', '')})" for k, v in c.get("currencies", {}).items()),
                "flag": c.get("flag", ""),
                "source": "restcountries.com",
            })
        return {"tool": "country_info", "country": country, "items": items}
    except Exception as exc:
        return err("country_info", exc)
