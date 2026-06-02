---
name: extract_citations
track: bonus
kind: local_analysis
requires_env: []
inputs: [text]
outputs: [citations, summary]
side_effect: false
---
# extract_citations

Extracts HTTP URLs and standalone arXiv identifiers from existing text. It
normalizes and deduplicates references but does not fetch or validate content.
