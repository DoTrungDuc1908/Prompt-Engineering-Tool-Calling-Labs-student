from __future__ import annotations

import re
import time
import unicodedata
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import requests


ROOT = Path(__file__).resolve().parents[1]
TIMEOUT = 30
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


def err(tool: str, exc: Exception) -> dict[str, Any]:
    return {"tool": tool, "error": type(exc).__name__, "message": str(exc)}


def request_with_retry(
    method: str,
    url: str,
    *,
    retries: int = 2,
    backoff_seconds: float = 0.5,
    **kwargs: Any,
) -> requests.Response:
    attempts = max(1, int(retries) + 1)
    for attempt in range(attempts):
        try:
            response = requests.request(method, url, **kwargs)
        except (requests.Timeout, requests.ConnectionError):
            if attempt == attempts - 1:
                raise
        else:
            if response.status_code not in RETRYABLE_STATUS_CODES or attempt == attempts - 1:
                return response
        time.sleep(backoff_seconds * (2 ** attempt))
    raise RuntimeError("request retry loop exhausted unexpectedly")


def domain(url: str) -> str:
    try:
        return urlparse(url).netloc.replace("www.", "")
    except Exception:
        return ""


def fold_text(text: str) -> str:
    decomposed = unicodedata.normalize("NFD", text.lower())
    folded = "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn")
    return folded.replace("đ", "d")


def terms(text: str) -> set[str]:
    stopwords = {
        "a", "an", "and", "are", "as", "at", "by", "for", "from", "in", "is", "of", "on", "or", "the", "to",
        "ban", "bao", "can", "cho", "co", "cua", "duoc", "gi", "giup", "la", "lam", "minh", "mot", "nay",
        "nen", "the", "thi", "trong", "va", "ve", "voi",
    }
    folded = fold_text(text)
    return {term for term in re.findall(r"[a-z0-9]+", folded) if len(term) > 1 and term not in stopwords}

