"""
AIService orchestrates prompt construction and LLM provider invocation.
"""
from typing import Optional
from app.providers.factory import get_llm_provider

class AIService:
    """
    Service layer for AI chat interactions.
    Handles prompt construction and provider invocation.
    """
    def __init__(self):
        self.provider = get_llm_provider()

    async def chat(self, user_message: str, rag_context: Optional[str] = None) -> str:
        """
        Build prompt and get LLM response.
        Args:
            user_message: The user's input message.
            rag_context: Optional RAG context string.
        Returns:
            LLM response as string.
        """
        prompt = self._build_prompt(user_message, rag_context)
        response = await self.provider.generate(prompt)
        return response

    def _build_prompt(self, user_message: str, rag_context: Optional[str]) -> str:
        """
        Construct the prompt for the LLM, optionally injecting RAG context.
        """
        if rag_context:
            return f"Context:\n{rag_context}\n\nUser: {user_message}\nAI:"
        return f"User: {user_message}\nAI:"

    async def chat_stream(self, user_message: str, rag_context: Optional[str] = None):
        """
        Stub for streaming support (not implemented yet).
        """
        raise NotImplementedError("Streaming not implemented yet.")
