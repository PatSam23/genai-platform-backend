from typing import List, Tuple, Dict, Any
from app.rag.retriever import Retriever

class RAGPipeline:
    """
    Orchestrates retrieval and context preparation for LLMs.
    """

    def __init__(self, retriever: Retriever):
        self.retriever = retriever

    async def run(
        self,
        query: str,
        top_k: int = 5,
    ) -> Tuple[str, List[Tuple[str, float]]]:
        """
        Returns:
        - context string to inject into prompt
        - retrieved documents with similarity scores
        """
        results = await self.retriever.retrieve(query, top_k=top_k)

        context = self._build_context(results)

        return context, results

    def _build_context(
        self,
        results: List[Tuple[str, float, Dict[str, Any]]],
    ) -> str:
        context_parts = []

        for i, (doc, score, metadata) in enumerate(results, start=1):
            meta_str = ", ".join(
                f"{k}={v}" for k, v in metadata.items()
            )

            context_parts.append(
                f"[Source {i} | score={score:.3f} | {meta_str}]\n{doc}"
            )

        return "\n\n".join(context_parts)
