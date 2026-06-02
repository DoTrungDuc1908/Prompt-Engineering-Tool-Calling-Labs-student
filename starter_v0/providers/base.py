from __future__ import annotations

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


def dedupe_tool_calls(calls: list[ToolCall]) -> list[ToolCall]:
    seen: list[ToolCall] = []
    for call in calls:
        if call not in seen:
            seen.append(call)
    return seen


def normalize_tool_calls(calls: list[ToolCall]) -> list[ToolCall]:
    # First, deduplicate exact duplicates
    deduped = dedupe_tool_calls(calls)
    
    # 1. Process extract_citations calls
    extract_calls = [c for c in deduped if c.name == "extract_citations"]
    kept_extract = []
    for c in extract_calls:
        text = c.args.get("text", "")
        is_sub = False
        for c_other in extract_calls:
            if c is c_other:
                continue
            other_text = c_other.args.get("text", "")
            if text in other_text and text != other_text:
                is_sub = True
                break
            elif text == other_text:
                # If texts are identical, keep the first one
                if extract_calls.index(c) > extract_calls.index(c_other):
                    is_sub = True
                    break
        if not is_sub:
            kept_extract.append(c)
            
    # 2. Process source_audit calls
    source_audit_calls = [c for c in deduped if c.name == "source_audit"]
    merged_source_audit = None
    if source_audit_calls:
        all_sources = []
        for c in source_audit_calls:
            sources = c.args.get("sources", [])
            for s in sources:
                if s not in all_sources:
                    all_sources.append(s)
        merged_source_audit = ToolCall(name="source_audit", args={"sources": all_sources})
        
    # 3. Assemble final list
    result = []
    source_audit_added = False
    for c in deduped:
        if c.name == "extract_citations":
            if c in kept_extract:
                result.append(c)
                # Remove to prevent duplicates
                kept_extract.remove(c)
        elif c.name == "source_audit":
            if not source_audit_added and merged_source_audit is not None:
                result.append(merged_source_audit)
                source_audit_added = True
        else:
            result.append(c)
    return result

