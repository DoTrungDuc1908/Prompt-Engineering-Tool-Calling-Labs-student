from __future__ import annotations

import os

from providers.openai_provider import OpenAIProvider


class OllamaProvider(OpenAIProvider):
    """Ollama local API — no real API key needed; uses dummy for OpenAI SDK compat."""

    def __init__(self) -> None:
        if not os.getenv("OLLAMA_API_KEY"):
            os.environ["OLLAMA_API_KEY"] = "ollama"
        super().__init__(
            api_key_env="OLLAMA_API_KEY",
            base_url="http://localhost:11434/v1",
            default_model="llama3.2",
        )
