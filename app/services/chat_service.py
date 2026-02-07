from typing import AsyncGenerator, List, Optional
from app.providers.factory import get_llm_provider
from app.models.chat import ChatMessage


class ChatService:
    def __init__(self):
        self.provider = get_llm_provider()

    # -------- PROMPT BUILDER --------
    def _build_prompt(
        self,
        prompt: str,
        history: List[ChatMessage],
        context: Optional[str] = None,
    ) -> str:
        convo = ""

        if context:
            convo += f"SYSTEM CONTEXT:\n{context}\n\n"

        for msg in history:
            convo += f"{msg.role.upper()}: {msg.content}\n"

        convo += f"USER: {prompt}\nASSISTANT:"
        return convo

    # -------- NON-STREAM --------
    async def generate(
        self,
        prompt: str,
        history: List[ChatMessage],
        context: Optional[str] = None,
    ) -> str:
        final_prompt = self._build_prompt(prompt, history, context)
        return await self.provider.generate(final_prompt)

    # -------- STREAM --------
    async def stream(
        self,
        prompt: str,
        history: List[ChatMessage],
        context: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        final_prompt = self._build_prompt(prompt, history, context)
        async for token in self.provider.stream(final_prompt):
            yield token
