---
name: briefing_outline
track: bonus
kind: local_formatter
requires_env: []
inputs: [items, audience, title]
outputs: [markdown, sections, summary]
side_effect: false
---
# briefing_outline

Builds a briefing outline from already-collected items. It includes evidence
placeholders and source-gap warnings but does not fetch or verify claims.
