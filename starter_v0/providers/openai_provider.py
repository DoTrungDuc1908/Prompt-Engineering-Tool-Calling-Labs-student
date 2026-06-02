from __future__ import annotations

import json
import os
import time
from typing import Any

from openai import APIError, RateLimitError
from providers.base import ModelResponse, ToolCall


class OpenAIProvider:
    """OpenAI Chat Completions provider with normalized tool_calls output and retry."""

    def __init__(
        self,
        *,
        api_key_env: str = "OPENAI_API_KEY",
        base_url: str | None = None,
        default_model: str = "gpt-4o-mini",
        max_retries: int = 3,
        retry_delay: float = 2.0,
    ) -> None:
        self.api_key_env = api_key_env
        self.base_url = base_url
        self.default_model = os.getenv("MODEL_NAME") or default_model
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    def _build_client(self) -> Any:
        from openai import OpenAI

        api_key = os.getenv(self.api_key_env)
        if not api_key:
            raise RuntimeError(f"Missing API key env var: {self.api_key_env}")
        return OpenAI(api_key=api_key, base_url=self.base_url)

    def complete(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]] | None = None,
        *,
        model: str | None = None,
        temperature: float = 0.0,
        tool_choice: Any | None = None,
    ) -> ModelResponse:
        client = self._build_client()
        kwargs: dict[str, Any] = {
            "model": model or self.default_model,
            "messages": messages,
            "temperature": temperature,
        }
        if tools:
            kwargs["tools"] = tools
        if tool_choice is not None:
            kwargs["tool_choice"] = tool_choice

        last_exc: Exception | None = None
        for attempt in range(self.max_retries):
            try:
                resp = client.chat.completions.create(**kwargs)
                msg = resp.choices[0].message
                calls: list[ToolCall] = []
                for call in msg.tool_calls or []:
                    args = json.loads(call.function.arguments or "{}")
                    calls.append(ToolCall(name=call.function.name, args=args))
                return ModelResponse(text=msg.content, tool_calls=calls, raw=resp)
            except RateLimitError as exc:
                last_exc = exc
                if attempt < self.max_retries - 1:
                    wait = self.retry_delay * (2 ** attempt)
                    time.sleep(wait)
            except APIError as exc:
                last_exc = exc
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
        raise last_exc  # type: ignore[misc]
