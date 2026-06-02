from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

# Folder names are intentionally vague to match the tool names students see.
# The imported function names are the underlying implementations (unchanged).
from .clarify.tool import ask_user
from .papers.tool import arxiv_search
from .paper_text.tool import get_arxiv_paper_text
from .timeline.tool import get_user_tweets
from .fetch.tool import read_url
from .format.tool import render_digest
from .policy.tool import search_company_policy
from .social_search.tool import search_tweets
from .send.tool import send_telegram
from .lookup.tool import web_search
from .wikipedia.tool import search_wikipedia
from .define.tool import define_word
from .hn_search.tool import search_hn
from .weather.tool import get_weather
from .country_info.tool import country_info
from .ip_info.tool import ip_lookup
from .math_calc.tool import calculate
from .hackernews.tool import top_hn_stories
from .exchange_rate.tool import exchange_rate
from .crypto_price.tool import crypto_price
from .get_time.tool import get_current_time
from .text_statistics.tool import get_text_statistics
from .sentiment_analysis.tool import analyze_sentiment
from .agent_memory.tool import manage_memory
from .export_report.tool import export_premium_report
from .visualize_data.tool import generate_svg_chart


# NOTE (starter_v0): tool names here are intentionally vague. These keys are the
# names the model sees AND the names data/eval_base.json + data/eval_research_extension.json
# match against. If a team renames a tool, it MUST stay in sync across ALL of:
#   artifacts/tools.yaml  ->  this dict  ->  data/eval_base.json + data/eval_research_extension.json
# Otherwise the eval raises "not declared in tools.yaml" or scores every call as a name mismatch.
TOOL_FUNCTIONS = {
    "clarify": ask_user,
    "timeline": get_user_tweets,
    "social_search": search_tweets,
    "lookup": web_search,
    "fetch": read_url,
    "format": render_digest,
    "send": send_telegram,
    "policy": search_company_policy,
    "papers": arxiv_search,
    "paper_text": get_arxiv_paper_text,
    "wikipedia": search_wikipedia,
    "define": define_word,
    "hn_search": search_hn,
    "weather": get_weather,
    "country_info": country_info,
    "ip_info": ip_lookup,
    "math_calc": calculate,
    "hackernews": top_hn_stories,
    "exchange_rate": exchange_rate,
    "crypto_price": crypto_price,
    "get_time": get_current_time,
    "text_statistics": get_text_statistics,
    "sentiment_analysis": analyze_sentiment,
    "agent_memory": manage_memory,
    "export_report": export_premium_report,
    "visualize_data": generate_svg_chart,
}


def load_tool_declarations(path: Path) -> list[dict[str, Any]]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))["tools"]


def to_openai_tools(declarations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{
        "type": "function",
        "function": {
            "name": item["name"],
            "description": item.get("description", ""),
            "parameters": item.get("parameters", {"type": "object", "properties": {}}),
        },
    } for item in declarations]

