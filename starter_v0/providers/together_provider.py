from __future__ import annotations

from providers.openai_provider import OpenAIProvider


class TogetherProvider(OpenAIProvider):
    def __init__(self) -> None:
        super().__init__(
            api_key_env="TOGETHER_API_KEY",
            base_url="https://api.together.xyz/v1",
            default_model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
        )
