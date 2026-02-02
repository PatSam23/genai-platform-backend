from abc import ABC, abstractmethod
from typing import List, Tuple, Dict, Any
import math
import chromadb
from chromadb.config import Settings as ChromaSettings

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
        metadatas: List[Dict[str, Any]],
    ) -> None:
        pass

    @abstractmethod
    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
    ) -> List[Tuple[str, float, Dict[str, Any]]]:
        pass

class InMemoryVectorStore(BaseVectorStore):
    def __init__(self):
        self._embeddings: List[List[float]] = []
        self._documents: List[str] = []
        self._metadatas: List[Dict[str, Any]] = []

    def add(
        self,
        embeddings: List[List[float]],
        documents: List[str],
        metadatas: List[Dict[str, Any]],
    ) -> None:
        if not (len(embeddings) == len(documents) == len(metadatas)):
            raise ValueError("Embeddings, documents, and metadatas must have same length")

        self._embeddings.extend(embeddings)
        self._documents.extend(documents)
        self._metadatas.extend(metadatas)

    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
    ) -> List[Tuple[str, float, Dict[str, Any]]]:
        scores = []

        for emb, doc, meta in zip(
            self._embeddings,
            self._documents,
            self._metadatas,
        ):
            similarity = cosine_similarity(query_embedding, emb)
            scores.append((doc, similarity, meta))

        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]
    


class ChromaVectorStore(BaseVectorStore):
    def __init__(self, persist_dir: str = "./chroma_db"):
        self.client = chromadb.Client(
            ChromaSettings(
                persist_directory=persist_dir,
                anonymized_telemetry=False,
            )
        )

        self.collection = self.client.get_or_create_collection(
            name="rag_documents"
        )

    def add(
        self,
        embeddings: List[List[float]],
        documents: List[str],
        metadatas: List[Dict[str, Any]],
    ) -> None:
        ids = [f"doc_{i}" for i in range(len(documents))]

        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )

        self.client.persist()

    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
    ) -> List[Tuple[str, float, Dict[str, Any]]]:
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
        )

        docs = results["documents"][0]
        metas = results["metadatas"][0]
        distances = results["distances"][0]

        # Convert distance → similarity
        similarities = [1 - d for d in distances]

        return list(zip(docs, similarities, metas))