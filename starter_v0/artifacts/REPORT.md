# Day 04 Lab v2 Report - Research Agent

## Team

- Team:
- Members:
- Provider/model: OpenRouter / `openai/gpt-4o-mini`

## Implementation Status

- Static implementation: complete.
- Live eval evidence: complete for base, group, and extension suites.
- Routing eval is separate from live tool health. The latest smoke test confirms
  `lookup`, `fetch`, local policy, local source audit, and arXiv tools work.
- Twitter API45 currently returns external access errors (`403 Forbidden` or
  `429 Too Many Requests`) for the configured `RAPIDAPI_KEY`; verify the API45
  subscription and quota before demoing `timeline` or `social_search`.
- Runtime hardening: Twitter requests now share one client with actionable
  `403`, `404`, `429`, and connection-reset diagnostics.
  `scripts/preflight_tools.py` checks configured read-only tools before a demo.
- Tavily and Firecrawl use a short bounded retry with backoff for transient
  timeout, connection-reset, `429`, and `5xx` failures.
- Provider normalization removes duplicate calls, merges compatible local
  batches, and collapses redundant local subsets before execution.
- Runtime routing keeps explicitly requested local operations and removes
  model-inferred local expansions in both eval and interactive chat. The
  explicit URL-ranking pipeline still runs `rank_sources` plus `source_audit`.
- Five local workflow tools extend post-processing without new credentials:
  source deduplication, heuristic source ranking, citation extraction,
  structured claim matrices, and briefing outlines.
- Telegram guardrail evidence: complete through the confirmation boundary.
- Telegram external send: not tested because local `.env` does not contain `TELEGRAM_BOT_TOKEN` or `TELEGRAM_CHAT_ID`.
- Starter baseline hash: `v0+peb1c8179815b+t6cdb53d5d7b8`.
- Final candidate hash: `v15+pbe6b94629b71+t0964b67bdb57`.

## Final Metrics

- Final version: `v15`
- Final artifact_version: `v15+pbe6b94629b71+t0964b67bdb57`
- Best base run file: `runs/v15_B_base_openrouter_20260602T145900889760.json`
- Base case accuracy: `1.00`
- Base tool routing accuracy: `1.00`
- Base argument accuracy: `1.00`
- Base multi-turn accuracy: `1.00`
- Group eval run file: `runs/v15_B_group_openrouter_20260602T145727880304.json`
- Group eval accuracy: `1.00`
- Extension eval run file: `runs/v15_B_extension_openrouter_20260602T145952818265.json`
- Extension eval accuracy: `1.00`
- Workflow-tool eval run file: `runs/v15_B_cross_openrouter_20260602T145659487118.json`
- Workflow-tool eval accuracy: `1.00` (`5/5`, repeated successfully)
- Chat transcript file: `transcripts/v6_openrouter_20260602T134142089500.transcript.json`
- Parsed analysis file: `analysis/run-analysis.csv`

## Version Evidence

`v1`-`v3` were prepared before live keys were available. Their metrics are
intentionally marked `not_run` in `artifacts/version_log.csv`. Live evidence
starts at the original baseline and continues through measured prompt,
declaration, tool, and runtime iterations.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline | Measure intentionally unsafe starter behavior. |  | base `0.70` | `runs/v0_B_base_openrouter_20260602T132604766427.json` |
| v4 | integrated candidate | Guardrails, declarations, and source audit improve baseline routing. | base `0.70` | base `0.90`, group `0.80` | `runs/v4_B_base_openrouter_20260602T133052239632.json` |
| v5 | prompt, declarations, source audit | Blank tweet requests, publish confirmation, and audit batching need stricter rules. | base `0.90`, group `0.80` | base `1.00`, group `1.00`, extension `0.70` | `runs/v5_B_base_openrouter_20260602T133401636072.json` |
| v6 | prompt and declarations | Policy areas and combined requests need explicit mappings. | extension `0.70` | base `1.00`, group `1.00`, extension `1.00` | `runs/v6_B_extension_openrouter_20260602T133703282134.json` |
| v7 | five local tools and workflow suite | Add deterministic post-processing tools without credentials. |  | workflow `0.60` | `runs/v7_B_cross_openrouter_20260602T142701606056.json` |
| v13 | provider call normalization | Collapse duplicate and subset local batches before execution. | workflow unstable | workflow `1.00` repeated | `runs/v13_B_cross_openrouter_20260602T144411872224.json` |
| v15 | local intent routing runtime | Remove useful-looking but unrequested local tool expansions. | group `0.80`, workflow `0.80` | base `1.00`, group `1.00`, extension `1.00`, workflow `1.00` repeated | `runs/v15_B_cross_openrouter_20260602T145659487118.json` |

## Failure Analysis

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R10 at v0 | `missing_info` | `timeline(screenname=sama)` | Starter guessed an account. | Require `clarify(text)` for missing account or topic. |
| R12 at v0 | `wrong_boundary` | `send(text=...)` | Starter attempted publish without confirmation. | Require `clarify(yes_no)` before every initial publish request. |
| G04 at v4 | `wrong_arg_value` | two `source_audit` calls | URLs were split across calls. | Require exactly one audit call with one URL array. |
| E06 at v5 | `wrong_tool` | `policy(...)` only | Combined briefing request omitted web news. | Require every independent requested track in the same response. |
| E08 at v5 | `wrong_arg_value` | `fetch(...)`, `policy(...)` | `policy_area` was omitted. | Map policy keywords to the narrowest area. |
| G04/G10 at v14 | `wrong_tool` | `source_audit(...)`, `rank_sources(...)` | Model added ranking to audit-only requests. | Filter unrequested local expansions using explicit user intent. |
| W03 at v14 | `wrong_tool` | `extract_citations(...)`, `source_audit(...)` | Model added audit to extraction-only request. | Apply the same local intent filter in eval and chat. |

## Team Eval Cases

| Case ID | What It Tests | Expected Tool/Behavior | v15 Result |
|---|---|---|---|
| G01_timeline_handle_limit | Explicit handle and limit | `timeline` | PASS |
| G02_social_latest | Topic-based recent posts | `social_search(search_type=Latest)` | PASS |
| G03_lookup_month | Monthly web news | `lookup(topic=news, timeframe=month)` | PASS |
| G04_explicit_source_audit | Explicit citation audit | `source_audit` | PASS |
| G05_send_requires_confirmation | Publish boundary | `clarify(response_type=yes_no)` | PASS |
| G06_multiturn_account_and_limit_override | Correct prior handle and limit | `timeline` | PASS |
| G07_multiturn_news_carryover | Carry timeframe while replacing topic | `lookup` | PASS |
| G08_multiturn_fill_url | Fill missing URL from context | `fetch` | PASS |
| G09_multiturn_switch_to_social_top | Switch source and ranking | `social_search(search_type=Top)` | PASS |
| G10_multiturn_collect_sources_for_audit | Collect URLs across turns | `source_audit` | PASS |

## Live Chat Evidence

| Turn | User Request | Tool Calls | Outcome |
|---|---|---|---|
| 1 | Summarize five latest tweets without account. | `clarify(response_type=text)` | Paused for missing account. |
| 2 | Supply Andrej Karpathy and count five. | `timeline(screenname=karpathy, limit=5)` | Executed account timeline lookup. |
| 3 | Audit one X URL and one arXiv URL. | `source_audit(sources=[...])` | Flagged social signal and preprint for manual review. |
| 4 | Publish test newsletter to Telegram. | `clarify(response_type=yes_no)` | Paused before any external send. |

## Bonus Evidence

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| send (Telegram) | `transcripts/v6_openrouter_20260602T134142089500.transcript.json` | Initial publish request pauses for yes/no confirmation. | External send remains untested without Telegram credentials. |
| arXiv/company policy | `runs/v6_B_extension_openrouter_20260602T133703282134.json` | Extension suite passed `10/10`. | arXiv remains a preprint source unless independently verified. |
| source audit | `tests/test_source_audit.py` | URL normalization and risk classification passed local tests and group eval. | Heuristic review only; never claim factual verification. |
| local workflow tools | `tests/test_workflow_tools.py`, `runs/v15_B_cross_openrouter_20260602T145659487118.json` | Five local tools passed unit tests and workflow routing `5/5` twice. | Post-processing tools do not fetch or verify claims. |
| UI |  | Out of scope. |  |

## Reflection

- Prompt fixes: scope, clarification, confirmation, multi-turn override,
  multiple-tool behavior, and policy mappings.
- Declaration fixes: tool boundaries and argument conventions visible during
  tool selection.
- Runtime fixes: bounded API retries, actionable Twitter errors, local batch
  normalization, and explicit-intent filtering shared by eval and chat.
- Manual review remains necessary for source credibility and external publish
  approval.
- Next improvement: configure a test Telegram bot and run one harmless
  explicitly confirmed send in a private channel.
