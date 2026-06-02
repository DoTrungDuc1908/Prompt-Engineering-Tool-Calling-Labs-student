from __future__ import annotations

import os
import time
from typing import Any

import requests

from tools._shared import TIMEOUT


DEFAULT_TWITTER_HOST = "twitter-api45.p.rapidapi.com"


def twitter_get(path: str, params: dict[str, Any]) -> dict[str, Any]:
    key = os.getenv("RAPIDAPI_KEY")
    host = os.getenv("RAPIDAPI_TWITTER_HOST", DEFAULT_TWITTER_HOST)
    if not key:
        raise RuntimeError("Missing RAPIDAPI_KEY env var")

    for attempt in range(2):
        try:
            response = requests.get(
                f"https://{host}{path}",
                params=params,
                headers={"x-rapidapi-key": key, "x-rapidapi-host": host},
                timeout=TIMEOUT,
            )
            break
        except (requests.Timeout, requests.ConnectionError) as exc:
            if attempt == 1:
                raise RuntimeError(f"Twitter API request failed for host {host}: {exc}") from exc
            time.sleep(0.5)
        except requests.RequestException as exc:
            raise RuntimeError(f"Twitter API request failed for host {host}: {exc}") from exc

    if response.status_code == 403:
        raise RuntimeError(
            f"Twitter API returned 403 Forbidden for host {host}. "
            "Verify that RAPIDAPI_KEY is subscribed to Twitter API45 and that "
            f"RAPIDAPI_TWITTER_HOST={DEFAULT_TWITTER_HOST}."
        )
    if response.status_code == 404:
        raise RuntimeError(
            f"Twitter API endpoint was not found on host {host}. "
            f"Set RAPIDAPI_TWITTER_HOST={DEFAULT_TWITTER_HOST} for the /timeline.php "
            "and /search.php endpoints."
        )
    if response.status_code == 429:
        raise RuntimeError(
            f"Twitter API returned 429 Too Many Requests for host {host}. "
            "Check the RapidAPI Twitter API45 quota and rate limit, then retry later."
        )

    response.raise_for_status()
    return response.json()
