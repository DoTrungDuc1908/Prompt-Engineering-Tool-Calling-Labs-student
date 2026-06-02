---
name: rank_sources
track: bonus
kind: local_analysis
requires_env: []
inputs: [items]
outputs: [items, summary, trust_boundary]
side_effect: false
---
# rank_sources

Ranks already-collected sources for manual review using transparent URL and
metadata heuristics. Scores are triage hints only. They do not verify claims or
establish source credibility.
