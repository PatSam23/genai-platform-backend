from abc import ABC, abstractmethod
from typing import List, Tuple
import math


def cosine_similarity(a: List[float], b: List[float]) -> float:
    dot_product = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot_product / (norm_a * norm_b)


class BaseVectorStore(ABC):
    @abstractmethod
    def add(
        self,
        embeddings: List[List[float]],
        documents: List[str],
    ) -> None:
        """
        Store embeddings with their corresponding documents.
        """
        pass

    @abstractmethod
    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
    ) -> List[Tuple[str, float]]:
        """
        Return top_k documents with similarity scores.
        """
        pass


class InMemoryVectorStore(BaseVectorStore):
    def __init__(self):
        self._embeddings: List[List[float]] = []
        self._documents: List[str] = []

    def add(
        self,
        embeddings: List[List[float]],
        documents: List[str],
    ) -> None:
        if len(embeddings) != len(documents):
            raise ValueError("Embeddings and documents must have same length")

        self._embeddings.extend(embeddings)
        self._documents.extend(documents)

    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
    ) -> List[Tuple[str, float]]:
        scores: List[Tuple[str, float]] = []

        for emb, doc in zip(self._embeddings, self._documents):
            similarity = cosine_similarity(query_embedding, emb)
            scores.append((doc, similarity))

        # Sort by similarity (higher is better)
        scores.sort(key=lambda x: x[1], reverse=True)

        return scores[:top_k]

