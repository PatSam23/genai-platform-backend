from typing import AsyncGenerator, List, Optional
from app.providers.factory import get_llm_provider
from app.models.chat import ChatMessage
from app.core.logging import setup_logger

logger = setup_logger(__name__, log_file="logs/chat_service.log")

class ChatService:
    def __init__(self):
        self.provider = get_llm_provider()
        logger.info(f"ChatService initialized with provider: {self.provider.__class__.__name__}")

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
        logger.debug(f"Generating response - prompt length: {len(prompt)}, history: {len(history)} messages")
        final_prompt = self._build_prompt(prompt, history, context)
        logger.debug(f"Built final prompt - length: {len(final_prompt)}")
        
        try:
            response = await self.provider.generate(final_prompt)
            logger.info(f"Response generated successfully - length: {len(response)}")
            return response
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}", exc_info=True)
            raise

    # -------- STREAM --------
    async def stream(
        self,
        prompt: str,
        history: List[ChatMessage],
        context: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        logger.debug(f"Starting streaming response - prompt length: {len(prompt)}, history: {len(history)} messages")
        final_prompt = self._build_prompt(prompt, history, context)
        logger.debug(f"Built final prompt for streaming - length: {len(final_prompt)}")
        
        token_count = 0
        try:
            async for token in self.provider.stream(final_prompt):
                token_count += 1
                yield token
            logger.info(f"Streaming completed - tokens generated: {token_count}")
        except Exception as e:
            logger.error(f"Error during streaming (after {token_count} tokens): {str(e)}", exc_info=True)
            raise
