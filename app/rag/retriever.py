from typing import List, Tuple

from app.rag.embeddings import BaseEmbeddingModel
from app.rag.vector_store import BaseVectorStore


class Retriever:
    """
    Orchestrates query embedding + vector search.
    """

    def __init__(
        self,
        embedding_model: BaseEmbeddingModel,
        vector_store: BaseVectorStore,
    ):
        self.embedding_model = embedding_model
        self.vector_store = vector_store

    async def retrieve(
        self,
        query: str,
        top_k: int = 5,
    ) -> List[Tuple[str, float]]:
        """
        Retrieve top-k relevant documents for a query.
        """
        query_embedding = (await self.embedding_model.embed([query]))[0]
        results = self.vector_store.search(query_embedding, top_k=top_k)
        return results
