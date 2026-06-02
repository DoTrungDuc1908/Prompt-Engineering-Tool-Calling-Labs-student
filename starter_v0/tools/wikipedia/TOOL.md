---
name: wikipedia
track: extra
kind: live_api
provider: MediaWiki
requires_env: []
inputs: [query, max_results]
outputs: [items]
side_effect: false
---
# wikipedia

Tra cứu nội dung từ Wikipedia. Không cần API key. Dùng MediaWiki API.
