from __future__ import annotations

import unittest

from providers.base import ToolCall
from tool_routing import filter_inferred_local_tool_calls


class FilterInferredLocalToolCallsTests(unittest.TestCase):
    def test_drops_rank_for_audit_only_request(self) -> None:
        calls = [
            ToolCall(name="source_audit", args={"sources": ["https://example.com"]}),
            ToolCall(name="rank_sources", args={"items": [{"url": "https://example.com"}]}),
        ]
        messages = [{"role": "user", "content": "Audit các nguồn citation này giúp mình."}]
        self.assertEqual(filter_inferred_local_tool_calls(calls, messages), [calls[0]])

    def test_allows_audit_pipeline_for_rank_request(self) -> None:
        calls = [
            ToolCall(name="rank_sources", args={"items": [{"url": "https://example.com"}]}),
            ToolCall(name="source_audit", args={"sources": ["https://example.com"]}),
        ]
        messages = [{"role": "user", "content": "Xếp hạng ưu tiên các nguồn này."}]
        self.assertEqual(filter_inferred_local_tool_calls(calls, messages), calls)

    def test_drops_audit_for_extract_only_request(self) -> None:
        calls = [
            ToolCall(name="extract_citations", args={"text": "See https://example.com"}),
            ToolCall(name="source_audit", args={"sources": ["https://example.com"]}),
        ]
        messages = [{"role": "user", "content": "Trích xuất citation từ đoạn text này."}]
        self.assertEqual(filter_inferred_local_tool_calls(calls, messages), [calls[0]])

    def test_keeps_non_local_research_calls(self) -> None:
        calls = [
            ToolCall(name="lookup", args={"query": "AI"}),
            ToolCall(name="source_audit", args={"sources": ["https://example.com"]}),
        ]
        messages = [{"role": "user", "content": "Trích xuất citation từ đoạn text này."}]
        self.assertEqual(filter_inferred_local_tool_calls(calls, messages), [calls[0]])

    def test_uses_previous_natural_user_intent_after_tool_results(self) -> None:
        calls = [
            ToolCall(name="source_audit", args={"sources": ["https://example.com"]}),
            ToolCall(name="rank_sources", args={"items": [{"url": "https://example.com"}]}),
        ]
        messages = [
            {"role": "user", "content": "Audit các nguồn citation này giúp mình."},
            {"role": "user", "content": "TOOL_RESULTS_JSON:\n[]"},
        ]
        self.assertEqual(filter_inferred_local_tool_calls(calls, messages), [calls[0]])


if __name__ == "__main__":
    unittest.main()
