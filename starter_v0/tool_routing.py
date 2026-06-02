from __future__ import annotations

import re
import unicodedata

from providers.base import ToolCall


LOCAL_POSTPROCESS_TOOLS = {
    "source_audit",
    "dedupe_sources",
    "rank_sources",
    "extract_citations",
    "claim_matrix",
    "briefing_outline",
}

_INTENT_PATTERNS = {
    "source_audit": (r"\baudit\b", r"citation risk", r"source risk", r"kiem tra (?:nguon|citation)"),
    "dedupe_sources": (r"\bdedup", r"\bduplicate", r"khu trung lap", r"\btrung lap\b"),
    "rank_sources": (r"\brank", r"\bpriorit", r"xep hang", r"\buu tien\b"),
    "extract_citations": (r"\bextract", r"trich xuat"),
    "claim_matrix": (r"claim matrix",),
    "briefing_outline": (r"\boutline\b",),
}


def _fold_text(text: str) -> str:
    folded = unicodedata.normalize("NFKD", text.lower())
    return "".join(char for char in folded if not unicodedata.combining(char)).replace("đ", "d")


def _explicit_local_intents(messages: list[dict[str, str]]) -> set[str]:
    for message in reversed(messages):
        if message.get("role") != "user":
            continue
        content = message.get("content", "")
        if content.startswith("TOOL_RESULTS_JSON:"):
            continue
        folded = _fold_text(content)
        intents = {
            name
            for name, patterns in _INTENT_PATTERNS.items()
            if any(re.search(pattern, folded) for pattern in patterns)
        }
        if intents:
            return intents
    return set()


def filter_inferred_local_tool_calls(calls: list[ToolCall], messages: list[dict[str, str]]) -> list[ToolCall]:
    """Remove unrequested local post-processing expansions while preserving research calls."""
    intents = _explicit_local_intents(messages)
    if not intents:
        return calls
    allowed = set(intents)
    if "rank_sources" in intents:
        allowed.add("source_audit")
    return [call for call in calls if call.name not in LOCAL_POSTPROCESS_TOOLS or call.name in allowed]
