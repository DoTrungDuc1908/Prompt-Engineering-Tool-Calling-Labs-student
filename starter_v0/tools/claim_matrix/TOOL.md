---
name: claim_matrix
track: bonus
kind: local_analysis
requires_env: []
inputs: [records]
outputs: [claims, summary, trust_boundary]
side_effect: false
---
# claim_matrix

Groups user-supplied structured claim records by normalized claim text and
collects supporting, disputing, and mentioning sources. It does not infer
stance from raw text or verify facts.
