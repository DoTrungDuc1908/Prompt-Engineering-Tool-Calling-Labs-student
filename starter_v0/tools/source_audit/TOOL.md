---
name: source_audit
track: bonus
kind: local_analysis
requires_env: []
inputs: [sources]
outputs: [results, summary, trust_boundary]
side_effect: false
---
# source_audit

Performs a deterministic heuristic review of user-supplied source URLs. It
normalizes URLs and flags invalid URLs, duplicates, social signals, and arXiv
preprints. It does not fetch content, verify factual claims, or replace company
policy search.
