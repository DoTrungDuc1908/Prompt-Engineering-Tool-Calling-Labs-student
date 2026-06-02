from __future__ import annotations

from providers.openai_provider import OpenAIProvider


class GroqProvider(OpenAIProvider):
    def __init__(self) -> None:
        super().__init__(
            api_key_env="GROQ_API_KEY",
            base_url="https://api.groq.com/openai/v1",
            default_model="llama-3.3-70b-versatile",
        )
