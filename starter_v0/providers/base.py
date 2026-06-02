from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass
class ToolCall:
    name: str
    args: dict[str, Any]


@dataclass
class ModelResponse:
    text: str | None = None
    tool_calls: list[ToolCall] = field(default_factory=list)
    raw: Any | None = None


def dedupe_tool_calls(calls: list[ToolCall]) -> list[ToolCall]:
    deduped: list[ToolCall] = []
    seen: set[tuple[str, str]] = set()
    for call in calls:
        key = (call.name, json.dumps(call.args, ensure_ascii=False, sort_keys=True, default=str))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(call)
    return deduped


def _is_redundant_batch_call(call: ToolCall, other: ToolCall) -> bool:
    if call.name != other.name:
        return False
    if call.name == "extract_citations":
        text = str(call.args.get("text") or "")
        other_text = str(other.args.get("text") or "")
        return bool(text) and text != other_text and text in other_text

    batch_keys = {
        "source_audit": "sources",
        "dedupe_sources": "items",
        "rank_sources": "items",
        "claim_matrix": "records",
        "briefing_outline": "items",
    }
    batch_key = batch_keys.get(call.name)
    if not batch_key:
        return False
    values = call.args.get(batch_key)
    other_values = other.args.get(batch_key)
    if not isinstance(values, list) or not isinstance(other_values, list) or len(values) >= len(other_values):
        return False
    normalized = {json.dumps(value, ensure_ascii=False, sort_keys=True, default=str) for value in values}
    other_normalized = {json.dumps(value, ensure_ascii=False, sort_keys=True, default=str) for value in other_values}
    return normalized.issubset(other_normalized)


def _merge_batch_tool_calls(calls: list[ToolCall]) -> list[ToolCall]:
    batch_keys = {
        "source_audit": "sources",
        "dedupe_sources": "items",
        "rank_sources": "items",
        "claim_matrix": "records",
        "briefing_outline": "items",
    }
    merged: list[ToolCall] = []
    merge_indexes: dict[tuple[str, str], int] = {}
    for call in calls:
        batch_key = batch_keys.get(call.name)
        values = call.args.get(batch_key) if batch_key else None
        if not batch_key or not isinstance(values, list):
            merged.append(call)
            continue

        options = {key: value for key, value in call.args.items() if key != batch_key}
        merge_key = (call.name, json.dumps(options, ensure_ascii=False, sort_keys=True, default=str))
        if merge_key not in merge_indexes:
            merge_indexes[merge_key] = len(merged)
            merged.append(ToolCall(name=call.name, args={**call.args, batch_key: list(values)}))
            continue

        existing = merged[merge_indexes[merge_key]]
        existing_values = existing.args[batch_key]
        seen = {json.dumps(value, ensure_ascii=False, sort_keys=True, default=str) for value in existing_values}
        for value in values:
            normalized = json.dumps(value, ensure_ascii=False, sort_keys=True, default=str)
            if normalized not in seen:
                existing_values.append(value)
                seen.add(normalized)
    return merged


def normalize_tool_calls(calls: list[ToolCall]) -> list[ToolCall]:
    deduped = _merge_batch_tool_calls(dedupe_tool_calls(calls))
    return [
        call
        for index, call in enumerate(deduped)
        if not any(
            _is_redundant_batch_call(call, other)
            for other_index, other in enumerate(deduped)
            if index != other_index
        )
    ]


class Provider(Protocol):
    def complete(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]] | None = None,
        *,
        model: str | None = None,
        temperature: float = 0.0,
        tool_choice: Any | None = None,
    ) -> ModelResponse:
        """Return normalized text/tool calls regardless of vendor API shape."""
