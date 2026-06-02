from __future__ import annotations

import unittest

from providers.base import ToolCall, dedupe_tool_calls, normalize_tool_calls


class DedupeToolCallsTests(unittest.TestCase):
    def test_removes_exact_duplicate_calls_and_preserves_order(self) -> None:
        calls = [
            ToolCall(name="extract_citations", args={"text": "one"}),
            ToolCall(name="extract_citations", args={"text": "one"}),
            ToolCall(name="extract_citations", args={"text": "two"}),
        ]
        self.assertEqual(dedupe_tool_calls(calls), [calls[0], calls[2]])

    def test_keeps_distinct_calls_with_same_name(self) -> None:
        calls = [
            ToolCall(name="fetch", args={"url": "https://example.com/a"}),
            ToolCall(name="fetch", args={"url": "https://example.com/b"}),
        ]
        self.assertEqual(dedupe_tool_calls(calls), calls)

    def test_collapses_extract_citation_subcalls_into_full_text_call(self) -> None:
        calls = [
            ToolCall(name="extract_citations", args={"text": "Read https://example.com and arXiv 1706.03762"}),
            ToolCall(name="extract_citations", args={"text": "https://example.com"}),
            ToolCall(name="extract_citations", args={"text": "1706.03762"}),
        ]
        self.assertEqual(normalize_tool_calls(calls), [calls[0]])

    def test_keeps_distinct_fetch_calls(self) -> None:
        calls = [
            ToolCall(name="fetch", args={"url": "https://example.com/a"}),
            ToolCall(name="fetch", args={"url": "https://example.com/b"}),
        ]
        self.assertEqual(normalize_tool_calls(calls), calls)

    def test_collapses_source_audit_subset_call(self) -> None:
        calls = [
            ToolCall(name="source_audit", args={"sources": ["https://example.com/a", "https://example.com/b"]}),
            ToolCall(name="source_audit", args={"sources": ["https://example.com/a"]}),
        ]
        self.assertEqual(normalize_tool_calls(calls), [calls[0]])

    def test_merges_disjoint_source_audit_calls(self) -> None:
        calls = [
            ToolCall(name="source_audit", args={"sources": ["https://example.com/a"]}),
            ToolCall(name="source_audit", args={"sources": ["https://example.com/b"]}),
        ]
        self.assertEqual(
            normalize_tool_calls(calls),
            [ToolCall(name="source_audit", args={"sources": ["https://example.com/a", "https://example.com/b"]})],
        )

    def test_keeps_batch_calls_with_distinct_options_separate(self) -> None:
        calls = [
            ToolCall(name="dedupe_sources", args={"items": [{"url": "https://example.com/a"}], "strategy": "url_only"}),
            ToolCall(name="dedupe_sources", args={"items": [{"title": "A"}], "strategy": "title_only"}),
        ]
        self.assertEqual(normalize_tool_calls(calls), calls)


if __name__ == "__main__":
    unittest.main()
