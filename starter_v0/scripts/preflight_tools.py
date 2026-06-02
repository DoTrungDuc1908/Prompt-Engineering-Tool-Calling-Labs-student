from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from env_loader import load_lab_env
from tools import TOOL_FUNCTIONS


load_lab_env(ROOT)


@dataclass(frozen=True)
class Check:
    name: str
    invoke: Callable[[], dict[str, Any]]


def item_count(result: dict[str, Any]) -> int | None:
    for key in ("items", "results"):
        items = result.get(key)
        if isinstance(items, list):
            return len(items)
    return None


def run_check(check: Check) -> bool:
    result = check.invoke()
    error = result.get("error")
    count = item_count(result)
    if error:
        print(f"FAIL {check.name}: {error}: {result.get('message', '')}")
        return False
    if count is not None and count == 0:
        print(f"FAIL {check.name}: returned no items")
        return False
    print(f"PASS {check.name}" + (f": items={count}" if count is not None else ""))
    return True


def checks(*, include_arxiv: bool, skip_twitter: bool) -> list[Check]:
    selected: list[Check] = []
    if not skip_twitter:
        selected.extend([
            Check("timeline", lambda: TOOL_FUNCTIONS["timeline"]("sama", limit=1)),
            Check("social_search", lambda: TOOL_FUNCTIONS["social_search"]("OpenAI", limit=1)),
        ])
    selected.extend([
        Check("lookup", lambda: TOOL_FUNCTIONS["lookup"]("OpenAI", max_results=1)),
        Check("fetch", lambda: TOOL_FUNCTIONS["fetch"]("https://openai.com/research/")),
        Check("format", lambda: TOOL_FUNCTIONS["format"]([{"title": "Preflight", "url": "https://example.com"}], template="brief")),
        Check("policy", lambda: TOOL_FUNCTIONS["policy"]("tweet viral fact", policy_area="source_citation", top_k=1)),
        Check("source_audit", lambda: TOOL_FUNCTIONS["source_audit"](["https://x.com/sama/status/1"])),
        Check("dedupe_sources", lambda: TOOL_FUNCTIONS["dedupe_sources"]([{"url": "https://example.com/?utm_source=one"}, {"url": "https://example.com/"}])),
        Check("rank_sources", lambda: TOOL_FUNCTIONS["rank_sources"]([{"url": "https://arxiv.org/abs/1706.03762"}])),
        Check("extract_citations", lambda: TOOL_FUNCTIONS["extract_citations"]("Source: https://example.com/report and arXiv 1706.03762")),
        Check("claim_matrix", lambda: TOOL_FUNCTIONS["claim_matrix"]([{"claim": "Example claim", "source": "https://example.com", "stance": "mentions"}])),
        Check("briefing_outline", lambda: TOOL_FUNCTIONS["briefing_outline"]([{"title": "Example", "url": "https://example.com"}])),
    ])
    if include_arxiv:
        selected.append(Check("papers", lambda: TOOL_FUNCTIONS["papers"]("AI agent evaluation", max_results=1)))
        selected.append(Check("paper_text", lambda: TOOL_FUNCTIONS["paper_text"]("1706.03762", max_pages=1)))
    return selected


def send_guardrail_ok() -> bool:
    result = TOOL_FUNCTIONS["send"]("preflight only: must not send", confirmed=False)
    if result.get("status") != "needs_confirmation":
        print(f"FAIL send guardrail: unexpected result {result}")
        return False
    print("PASS send guardrail: blocked without confirmation")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Smoke-test configured read-only research tools.")
    parser.add_argument("--include-arxiv", action="store_true", help="Also call rate-limited arXiv tools.")
    parser.add_argument("--skip-twitter", action="store_true", help="Skip Twitter API45 while diagnosing external access or quota.")
    args = parser.parse_args()

    failed_required = [
        check.name
        for check in checks(include_arxiv=args.include_arxiv, skip_twitter=args.skip_twitter)
        if not run_check(check)
    ]
    if not send_guardrail_ok():
        failed_required.append("send_guardrail")
    if failed_required:
        raise SystemExit(f"Tool preflight failed: {', '.join(failed_required)}")
    print("Tool preflight passed.")


if __name__ == "__main__":
    main()
