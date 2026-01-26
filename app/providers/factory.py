# Factory for selecting and returning the configured LLM provider

from app.core.config import settings  # application configuration / runtime settings
from app.providers.base import BaseLLMProvider  # provider interface / base class
from app.providers.ollama import OllamaProvider  # Ollama provider implementation


def get_llm_provider() -> BaseLLMProvider:
    """Instantiate and return the LLM provider specified in settings."""
    if settings.LLM_PROVIDER == "ollama":
        return OllamaProvider()

    # Unknown provider configured — surface a clear error
    raise ValueError(f"Unsupported LLM provider: {settings.LLM_PROVIDER}")
