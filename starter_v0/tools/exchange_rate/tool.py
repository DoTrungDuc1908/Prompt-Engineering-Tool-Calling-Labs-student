from __future__ import annotations

from typing import Any

import requests

from tools._shared import err


def exchange_rate(base: str = "USD", target: str = "EUR", amount: float = 1.0) -> dict[str, Any]:
    try:
        resp = requests.get(f"https://api.frankfurter.app/latest", params={"from": base, "to": target}, timeout=15)
        if resp.status_code == 404:
            return {"tool": "exchange_rate", "base": base, "target": target, "items": []}
        resp.raise_for_status()
        data = resp.json()
        rate = data.get("rates", {}).get(target, 0)
        converted = round(amount * rate, 4) if rate else 0
        return {"tool": "exchange_rate", "base": base, "target": target, "items": [{
            "base": base,
            "target": target,
            "rate": rate,
            "amount": amount,
            "converted": converted,
            "date": data.get("date", ""),
            "source": "frankfurter.app (ECB)",
        }]}
    except Exception as exc:
        return err("exchange_rate", exc)
