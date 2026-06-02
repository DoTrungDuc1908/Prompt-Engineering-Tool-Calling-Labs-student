from __future__ import annotations

import unittest

from tools.briefing_outline.tool import build_briefing_outline
from tools.claim_matrix.tool import build_claim_matrix
from tools.dedupe_sources.tool import dedupe_sources
from tools.extract_citations.tool import extract_citations
from tools.rank_sources.tool import rank_sources


class DedupeSourcesTests(unittest.TestCase):
    def test_removes_normalized_url_duplicates(self) -> None:
        result = dedupe_sources([
            {"title": "One", "url": "https://example.com/report?utm_source=mail"},
            {"title": "Two", "url": "https://EXAMPLE.com/report"},
        ])
        self.assertEqual(result["summary"], {"input_count": 2, "unique_count": 1, "removed_count": 1})
        self.assertEqual(result["duplicate_groups"][0]["duplicate_indexes"], [1])

    def test_falls_back_to_folded_title(self) -> None:
        result = dedupe_sources([{"title": "Bao cao AI"}, {"title": "Báo cáo AI"}])
        self.assertEqual(result["summary"]["removed_count"], 1)


class RankSourcesTests(unittest.TestCase):
    def test_prioritizes_declared_primary_over_social_signal(self) -> None:
        result = rank_sources([
            {"url": "https://x.com/sama/status/1"},
            {"url": "https://openai.com/research/", "source_type": "official"},
        ])
        self.assertEqual(result["items"][0]["normalized_url"], "https://openai.com/research")
        self.assertIn("social_signal_only", result["items"][1]["reasons"])
        self.assertTrue(all(item["requires_review"] for item in result["items"]))


class ExtractCitationsTests(unittest.TestCase):
    def test_extracts_normalized_url_and_standalone_arxiv_id(self) -> None:
        result = extract_citations(
            "Read https://example.com/report?utm_source=mail. "
            "Duplicate https://EXAMPLE.com/report and paper 1706.03762."
        )
        self.assertEqual(result["summary"], {"total": 2, "urls": 1, "standalone_arxiv_ids": 1})
        self.assertEqual(result["citations"][0]["url"], "https://example.com/report")
        self.assertEqual(result["citations"][1]["url"], "https://arxiv.org/abs/1706.03762")


class ClaimMatrixTests(unittest.TestCase):
    def test_groups_folded_claims_and_flags_conflict(self) -> None:
        result = build_claim_matrix([
            {"claim": "Mô hình đạt 90%", "source": "source-a", "stance": "supports"},
            {"claim": "Mo hinh dat 90%", "source": "source-b", "stance": "disputes"},
        ])
        self.assertEqual(result["summary"]["claim_count"], 1)
        self.assertEqual(result["summary"]["conflict_count"], 1)
        self.assertTrue(result["claims"][0]["has_conflict"])


class BriefingOutlineTests(unittest.TestCase):
    def test_builds_technical_outline_and_reports_source_gap(self) -> None:
        result = build_briefing_outline(
            [{"title": "Paper"}, {"title": "Docs", "url": "https://example.com/docs"}],
            audience="technical",
            title="AI scan",
        )
        self.assertIn("# AI scan", result["markdown"])
        self.assertIn("## Limitations", result["markdown"])
        self.assertEqual(result["summary"], {"item_count": 2, "missing_source_count": 1})


if __name__ == "__main__":
    unittest.main()
