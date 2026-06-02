from __future__ import annotations

from providers.openai_provider import OpenAIProvider


class NvidiaProvider(OpenAIProvider):
    def __init__(self) -> None:
        super().__init__(
            api_key_env="NVIDIA_API_KEY",
            base_url="https://integrate.api.nvidia.com/v1",
            default_model="meta/llama-3.1-405b-instruct",
        )
