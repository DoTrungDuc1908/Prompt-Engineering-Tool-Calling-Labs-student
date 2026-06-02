---
name: dedupe_sources
track: bonus
kind: local_analysis
requires_env: []
inputs: [items, strategy]
outputs: [items, duplicate_groups, summary]
side_effect: false
---
# dedupe_sources

Removes duplicate already-collected research items using normalized URLs or
titles. It does not fetch content or decide whether two differently-worded
claims are equivalent.
