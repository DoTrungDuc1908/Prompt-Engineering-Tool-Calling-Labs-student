from providers.openai_provider import OpenAIProvider
from providers.openrouter_provider import OpenRouterProvider
from providers.anthropic_provider import AnthropicProvider
from providers.gemini_provider import GeminiProvider
from providers.ollama_provider import OllamaProvider
from providers.nvidia_provider import NvidiaProvider
from providers.together_provider import TogetherProvider
from providers.groq_provider import GroqProvider
from providers.deepseek_provider import DeepSeekProvider


def make_provider(name: str):
    if name == "openai":
        return OpenAIProvider()
    if name == "openrouter":
        return OpenRouterProvider()
    if name == "anthropic":
        return AnthropicProvider()
    if name == "gemini":
        return GeminiProvider()
    if name == "ollama":
        return OllamaProvider()
    if name == "nvidia":
        return NvidiaProvider()
    if name == "together":
        return TogetherProvider()
    if name == "groq":
        return GroqProvider()
    if name == "deepseek":
        return DeepSeekProvider()
    raise ValueError(f"Unknown provider: {name}")
