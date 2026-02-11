import ollama
from typing import AsyncGenerator
from app.providers.base import BaseLLMProvider
from app.core.config import settings
from app.core.logging import setup_logger

logger = setup_logger(__name__, log_file="logs/ollama.log")

class OllamaProvider(BaseLLMProvider):
    async def generate(self, prompt: str, context: str | None = None) -> str:
        logger.debug(f"Generating with Ollama - model: {settings.OLLAMA_MODEL}, prompt length: {len(prompt)}")
        messages = []

        if context:
            logger.debug(f"Using context - length: {len(context)}")
            messages.append({
                "role": "system",
                "content": f"Use the following context to answer:\n{context}, DO not use any information outside of this context. If you don't know the answer, say you don't know. Do not make up an answer. Only use the information provided in the context. DO not make up any names."
            })

        messages.append({"role": "user", "content": prompt})
        
        try:
            response = ollama.chat(
                model=settings.OLLAMA_MODEL,
                messages=messages,
                options={"temperature": settings.OLLAMA_TEMPERATURE},
            )
            result = response["message"]["content"]
            logger.info(f"Ollama response generated - length: {len(result)}")
            return result
        except Exception as e:
            logger.error(f"Error generating with Ollama: {str(e)}", exc_info=True)
            raise

    async def stream(
        self, prompt: str, context: str | None = None
    ) -> AsyncGenerator[str, None]:
        logger.debug(f"Streaming with Ollama - model: {settings.OLLAMA_MODEL}, prompt length: {len(prompt)}")
        messages = []

        if context:
            logger.debug(f"Using context for streaming - length: {len(context)}")
            messages.append({
                "role": "system",
                "content": f"Use the following context to answer:\n{context}, DO not use any information outside of this context. If you don't know the answer, say you don't know. Do not make up an answer. Only use the information provided in the context. DO not make up any names."
            })

        messages.append({"role": "user", "content": prompt})

        token_count = 0
        try:
            for chunk in ollama.chat(
                model=settings.OLLAMA_MODEL,
                messages=messages,
                options={"temperature": settings.OLLAMA_TEMPERATURE},
                stream=True,
            ):
                if "message" in chunk and "content" in chunk["message"]:
                    token_count += 1
                    yield chunk["message"]["content"]
            logger.info(f"Ollama streaming completed - tokens: {token_count}")
        except Exception as e:
            logger.error(f"Error streaming with Ollama (after {token_count} tokens): {str(e)}", exc_info=True)
            raise
