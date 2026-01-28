from typing import AsyncGenerator
from app.providers.factory import get_llm_provider


class AIService:
    def __init__(self):
        self.provider = get_llm_provider()

    async def generate_response(
        self, prompt: str, context: str | None = None
    ) -> str:
        final_prompt = self._build_prompt(prompt)
        return await self.provider.generate(final_prompt, context)

    async def stream_response(
        self, prompt: str, context: str | None = None
    ) -> AsyncGenerator[str, None]:
        final_prompt = self._build_prompt(prompt)
        async for token in self.provider.stream(final_prompt, context):
            yield token

    def _build_prompt(self, prompt: str) -> str:
        return f"You are a helpful AI assistant.\nUser: {prompt}\nAssistant:"
