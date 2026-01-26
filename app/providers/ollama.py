import ollama
from app.providers.base import BaseLLMProvider
from app.core.config import settings


class OllamaProvider(BaseLLMProvider):
    async def generate(self, prompt: str, context: str | None = None) -> str:
        """
        Generate a response from the Ollama LLM.
        Args:
            prompt: The full prompt string (already constructed).
            context: Deprecated. Not used; prompt should include context if needed.
        Returns:
            LLM response as string.
        """
        messages = [
            {"role": "user", "content": prompt}
        ]
        response = ollama.chat(
            model=settings.OLLAMA_MODEL,
            messages=messages,
            options={
                "temperature": settings.OLLAMA_TEMPERATURE
            }
        )
        return response["message"]["content"]
