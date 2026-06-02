from __future__ import annotations

from typing import Any

import requests

from tools._shared import err


def ip_lookup(ip: str = "") -> dict[str, Any]:
    try:
        resp = requests.get(f"http://ip-api.com/json/{ip}", timeout=15)
        resp.raise_for_status()
        data = resp.json()
        if data.get("status") == "fail":
            return {"tool": "ip_lookup", "ip": ip, "items": []}
        return {"tool": "ip_lookup", "ip": ip, "items": [{
            "ip": data.get("query", ip),
            "country": data.get("country", ""),
            "region": data.get("regionName", ""),
            "city": data.get("city", ""),
            "zip": data.get("zip", ""),
            "lat": data.get("lat"),
            "lon": data.get("lon"),
            "isp": data.get("isp", ""),
            "org": data.get("org", ""),
            "source": "ip-api.com",
        }]}
    except Exception as exc:
        return err("ip_lookup", exc)
