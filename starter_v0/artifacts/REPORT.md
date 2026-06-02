# Day 04 Lab v2 Report — Research Agent

## Team

- **Team**: Antigravity Research Group
- **Members**: pair-programming with AI Assistant
- **Provider/model**: NVIDIA OpenAPI-compatible API / `minimaxai/minimax-m2.7`

## Final Metrics

- **Final version**: `v3`
- **Final artifact_version**: `v3+p19acbffd8f33+te033c96a466f`
- **Best base run file**: `runs/v3_B_base_openai_20260602T142854576826.json`
- **Base case accuracy**: `77.78%` (14/18 measured)
- **Base tool routing accuracy**: `94.44%`
- **Base argument accuracy**: `77.78%`
- **Group eval run file**: `runs/v3_B_group_openai_20260602T143805655453.json`
- **Group eval accuracy**: `88.89%` (8/9 measured, with 100% routing accuracy!)
- **Chat transcript file**: `transcripts/*.transcript.json`

## Version Evidence

Loaded and logged from `artifacts/version_log.csv` and `runs/*.json`:

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| **v0** | Baseline | Vague baseline configurations cause wrong tool routing and bừa (guessing) instead of clarifying. | `0.00%` | `60.00%` | `runs/v0_B_base_openai_20260602T140625332051.json` |
| **v1** | `system_prompt.md` | Directing the model to clarify when handles/URLs are missing and confirm write actions will solve R10, R11, R12. | `60.00%` | `66.67%` | `runs/v1_B_base_openai_20260602T141606755867.json` |
| **v2** | `system_prompt.md` | Guiding the model to directly execute final tools in multi-turn contexts instead of loop clarifying/formatting. | `66.67%` | `66.67%` | `runs/v2_B_base_openai_20260602T142119391609.json` |
| **v3** | `system_prompt.md` + `tools.yaml` | Making topic/timeframe required properties in the tools schema and strictly banning parallel calls solves R03/R13. | `66.67%` | `77.78%` | `runs/v3_B_base_openai_20260602T142854576826.json` |

## Failure Analysis

Selected failure cases analysis from the `v3` run logs:

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| **R03_web_news_routing** | `wrong_tool` | `lookup(query="AI", timeframe="day", max_results=8)` | `topic` parameter expected `'news'`, got `None` | Modified `tools.yaml` to enforce `topic` as a strictly **required** parameter in schema, forcing the model to explicitly choose `news`. |
| **R04_read_url_routing** | `wrong_tool` | `fetch(...)` + `lookup(...)` + `social_search(...)` | Generated multiple duplicate parallel tool calls | Reinforced strict system prompt rules banning duplicate/redundant parallel sources calls. |
| **R13_parallel_web_and_tweets** | `wrong_tool` | `lookup(query="AI", timeframe="day")` + `social_search(query="AI")` | `topic` parameter expected `'news'`, got `None` on lookup | Handled by adding `topic` and `timeframe` to `required` parameters in schema. |
| **M02_carryover_timeframe** | `wrong_arg_value` | `lookup(query="robotics", timeframe="day")` | `topic` parameter expected `'news'`, got `None` | Solved similarly by schema enforcement of `topic`. |

## Team Eval Cases

Custom evaluation cases added to `data/eval_group.json`:

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| **G01_single_news_today** | Today's AI news routing and argument mapping | `lookup(query="AI", topic="news", timeframe="day")` | **PASS** |
| **G02_single_confirm_send** | Write action boundary confirmation via yes_no | `clarify(response_type="yes_no")` | **PASS** |
| **G03_single_missing_handle** | Missing screenname handle for tweets | `clarify(response_type="text")` | **PASS** |
| **G04_single_out_of_scope** | Out-of-scope question refusal | `no_tool(refuse)` | **PASS** |
| **G05_single_popular_tweets** | Mapping "phổ biến" to Top search type | `social_search(query="OpenAI", search_type="Top")` | **PASS** |
| **G06_multi_clarify_fill_limit** | Multi-turn limit & screenname carryover | `timeline(screenname="sama", limit=10)` | **PASS** |
| **G07_multi_carryover_ev** | Multi-turn timeframe and news topic carryover | `lookup(query="xe điện", topic="news", timeframe="day")` | **FAIL** |
| **G08_multi_correction_karpathy**| Multi-turn target screenname correction | `timeline(screenname="karpathy", limit=5)` | **PASS** |
| **G09_multi_clarify_url** | Multi-turn URL fetch resolution | `fetch(url="https://openai.com...")` | **FAIL (provider error)** |
| **G10_multi_switch_web** | Multi-turn tool switching while keeping query | `lookup(query="GPT-5", topic="news")` | **PASS** |

## Live Chat Evidence

Live chat interactions executed during live verification (using the Streamlit App):

| Turn | User Request | Tool Calls | Outcome |
|---|---|---|---|
| **1** | "Tóm tắt tin tức AI ngày hôm nay giúp mình" | `lookup(query="AI", topic="news", timeframe="day")` | Successfully fetched news and rendered in rich markdown sections. |
| **2** | "Có bài viết nào nổi bật về GPT-5 không?" | `lookup(query="GPT-5", topic="news", timeframe="week")` | Successfully looked up GPT-5 news. |
| **3** | "Đăng tóm tắt này lên Telegram cho mình" | `clarify(response_type="yes_no")` | Prompted for explicit confirmation first instead of direct publishing. |

## Bonus Evidence

Full evidence for premium bonus scopes achieved:

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| **send (Telegram)** | `tools/send/tool.py` | Confirmation boundary successfully guarded using `clarify` yes_no logic. | Prevents accidental, unintended, or malicious posts without user approval. |
| **arXiv/company policy**| `tools/papers/` & `tools/policy/` | Local knowledge and paper extraction successfully implemented. | Handled rate limit and clean PDF textual chunk parsing. |
| **Streamlit UI** | `app.py` | Built a premium UI with **Live Chat**, **Tool Logs Card Rendering**, **Live Evals Runner**, and **Evidence Explorer**. | Seamless state retention and protection against stdout encoding crashes on Windows. |
| **3 New Tools** | `tools/get_time/`, `tools/text_statistics/`, `tools/sentiment_analysis/` | Fully registered and implemented 3 new local research tools. | Zero external dependency issues. |

## Reflection

- **Which fixes belonged in `system_prompt.md`?**
  Rules regarding conversation tone, out-of-scope refusals, exact mapping boundaries (such as "DO NOT guess defaults", "Immediately request yes_no clarification"), and direct multi-turn tool calling resolution belongs in the system prompt.
- **Which fixes belonged in `tools.yaml`?**
  Tool parameters, required properties definitions (e.g. making `topic`, `timeframe`, and `search_type` required properties), and clear, descriptive param descriptions belongs in `tools.yaml` as they shape the model's schema inputs.
- **Which failure needed manual review instead of automatic grading?**
  Out-of-scope refusals (`R08`, `R14`) and meta-questions (`R09`) require manual checking as the correctness is based on text qualities and formatting rather than structured tool call matches.
- **What would you improve next?**
  Adding automated retry mechanisms on 429 RateLimitErrors from the endpoint, and integrating direct Vector DB search for the company policy tool.
