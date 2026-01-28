import ollama
from typing import AsyncGenerator
from app.providers.base import BaseLLMProvider
from app.core.config import settings


class OllamaProvider(BaseLLMProvider):
    async def generate(self, prompt: str, context: str | None = None) -> str:
        messages = []

        if context:
            messages.append({
                "role": "system",
                "content": f"Use the following context to answer:\n{context}"
            })

        messages.append({"role": "user", "content": prompt})
        response = ollama.chat(
            model=settings.OLLAMA_MODEL,
            messages=messages,
            options={"temperature": settings.OLLAMA_TEMPERATURE},
        )

        return response["message"]["content"]

    async def stream(
        self, prompt: str, context: str | None = None
    ) -> AsyncGenerator[str, None]:
        messages = []

        if context:
            messages.append({
                "role": "system",
                "content": f"Use the following context to answer:\n{context}"
            })

        messages.append({"role": "user", "content": prompt})

        for chunk in ollama.chat(
            model=settings.OLLAMA_MODEL,
            messages=messages,
            options={"temperature": settings.OLLAMA_TEMPERATURE},
            stream=True,
        ):
            if "message" in chunk and "content" in chunk["message"]:
                yield chunk["message"]["content"]
