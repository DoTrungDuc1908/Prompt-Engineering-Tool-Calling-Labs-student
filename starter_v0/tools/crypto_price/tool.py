from __future__ import annotations

from typing import Any

import requests

from tools._shared import err


def crypto_price(coin: str = "bitcoin", vs_currency: str = "usd") -> dict[str, Any]:
    try:
        resp = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": coin, "vs_currencies": vs_currency, "include_market_cap": "true", "include_24hr_change": "true"},
            timeout=15,
        )
        if resp.status_code == 429:
            return {"tool": "crypto_price", "coin": coin, "items": [], "note": "rate_limited"}
        if resp.status_code == 404:
            return {"tool": "crypto_price", "coin": coin, "items": []}
        resp.raise_for_status()
        data = resp.json().get(coin, {})
        price = data.get(vs_currency)
        if price is None:
            return {"tool": "crypto_price", "coin": coin, "items": []}
        return {"tool": "crypto_price", "coin": coin, "items": [{
            "coin": coin,
            "price": price,
            "currency": vs_currency.upper(),
            "market_cap": data.get(f"{vs_currency}_market_cap"),
            "change_24h": data.get(f"{vs_currency}_24h_change"),
            "source": "coingecko.com",
        }]}
    except Exception as exc:
        return err("crypto_price", exc)
