import ollama
from app.providers.base import BaseLLMProvider
from app.core.config import settings


class OllamaProvider(BaseLLMProvider):
    async def generate(self, prompt: str, context: str | None = None) -> str:
        messages = []

        # If RAG context is provided, inject it as system message
        if context:
            messages.append({
                "role": "system",
                "content": f"Use the following context to answer:\n{context}"
            })

        messages.append({
            "role": "user",
            "content": prompt
        })

        response = ollama.chat(
            model=settings.OLLAMA_MODEL,
            messages=messages,
            options={
                "temperature": settings.OLLAMA_TEMPERATURE
            }
        )

        return response["message"]["content"]
