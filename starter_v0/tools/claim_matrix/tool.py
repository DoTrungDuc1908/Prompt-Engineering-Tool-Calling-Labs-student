from __future__ import annotations

import re
from typing import Any

from tools._shared import fold_text


VALID_STANCES = {"supports", "disputes", "mentions"}


def _claim_key(claim: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", fold_text(claim)).strip()


def build_claim_matrix(records: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    grouped: dict[str, dict[str, Any]] = {}
    for record in records or []:
        claim = str(record.get("claim") or "").strip()
        source = str(record.get("source") or "").strip()
        stance = str(record.get("stance") or "mentions").strip().lower()
        if not claim or not source:
            continue
        if stance not in VALID_STANCES:
            stance = "mentions"
        key = _claim_key(claim)
        entry = grouped.setdefault(key, {
            "claim": claim,
            "supports": [],
            "disputes": [],
            "mentions": [],
        })
        if source not in entry[stance]:
            entry[stance].append(source)

    claims: list[dict[str, Any]] = []
    for entry in grouped.values():
        claims.append({
            **entry,
            "has_conflict": bool(entry["supports"] and entry["disputes"]),
        })
    return {
        "tool": "claim_matrix",
        "claims": claims,
        "summary": {
            "claim_count": len(claims),
            "record_count": sum(len(item[stance]) for item in claims for stance in VALID_STANCES),
            "conflict_count": sum(item["has_conflict"] for item in claims),
        },
        "trust_boundary": (
            "This matrix organizes user-supplied stances only. It does not "
            "infer stance from raw text or verify factual claims."
        ),
    }
