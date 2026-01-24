from abc import ABC, abstractmethod

class BaseLLMProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str, context: str | None = None):
        pass
