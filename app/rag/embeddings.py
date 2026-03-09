from abc import ABC, abstractmethod
from typing import List
import ollama
from app.core.config import settings

class BaseEmbeddingModel(ABC):
    """
    Contract for any embedding model used in the RAG pipeline.

    Responsibility:
    - Convert text into numerical vectors
    - No storage
    - No retrieval
    - No chunking logic
    """

    @abstractmethod
    async def embed(self, texts: List[str]) -> List[List[float]]:
        """
        Convert a list of texts into embedding vectors.

        Args:
            texts: List of input strings (chunks or queries)

        Returns:
            List of embedding vectors (one per input text)
        """
        pass


class OllamaEmbeddingModel(BaseEmbeddingModel):
    """
    Ollama-based embedding implementation.

    NOTE:
    - Uses Ollama's async embedding API (ollama 0.4+)
    - Currently uses settings.OLLAMA_MODEL
    - Will be split into a dedicated embedding model later
    """

    async def embed(self, texts: List[str]) -> List[List[float]]:
        client = ollama.AsyncClient()
        # ollama.AsyncClient.embed() accepts a list of inputs and returns
        # an EmbedResponse with .embeddings: list[list[float]]
        response = await client.embed(
            model=settings.OLLAMA_MODEL,
            input=texts,
        )
        return response.embeddings
