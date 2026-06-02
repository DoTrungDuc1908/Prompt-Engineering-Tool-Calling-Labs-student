from __future__ import annotations

from providers.openai_provider import OpenAIProvider


class DeepSeekProvider(OpenAIProvider):
    def __init__(self) -> None:
        super().__init__(
            api_key_env="DEEPSEEK_API_KEY",
            base_url="https://api.deepseek.com",
            default_model="deepseek-chat",
        )
