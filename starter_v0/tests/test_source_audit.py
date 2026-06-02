from __future__ import annotations

import unittest

from tools.source_audit.tool import audit_sources, normalize_url


class NormalizeUrlTests(unittest.TestCase):
    def test_normalizes_host_tracking_query_fragment_and_trailing_slash(self) -> None:
        actual = normalize_url(" HTTPS://Example.COM/report/?utm_source=mail&b=2&a=1#section ")
        self.assertEqual(actual, "https://example.com/report?a=1&b=2")

    def test_rejects_invalid_url(self) -> None:
        self.assertEqual(normalize_url("not a URL"), "")


class AuditSourcesTests(unittest.TestCase):
    def test_flags_duplicates_after_normalization(self) -> None:
        result = audit_sources([
            "https://example.com/report?utm_source=mail",
            "https://EXAMPLE.com/report",
        ])
        self.assertEqual(result["summary"]["duplicates"], 1)
        self.assertIn("duplicate_url", result["results"][0]["issues"])
        self.assertIn("duplicate_url", result["results"][1]["issues"])

    def test_flags_social_signal_preprint_and_invalid_url(self) -> None:
        result = audit_sources([
            "https://x.com/sama/status/1",
            "https://arxiv.org/abs/1706.03762",
            "broken",
        ])
        self.assertEqual(result["summary"]["social_signals"], 1)
        self.assertEqual(result["summary"]["preprints"], 1)
        self.assertEqual(result["summary"]["invalid_urls"], 1)
        self.assertEqual(
            [item["category"] for item in result["results"]],
            ["social_signal", "preprint", "invalid_url"],
        )

    def test_treats_singleton_string_as_one_source(self) -> None:
        result = audit_sources("https://example.com/report")
        self.assertEqual(result["summary"]["total"], 1)
        self.assertEqual(result["results"][0]["normalized_url"], "https://example.com/report")


if __name__ == "__main__":
    unittest.main()
