from typing import AsyncGenerator
from app.providers.factory import get_llm_provider
from app.rag.pipeline import RAGPipeline
from app.rag.retriever import Retriever
from app.rag.embeddings import OllamaEmbeddingModel
from app.rag.vector_store import InMemoryVectorStore
from app.rag.chunking import chunk_text
from app.rag.schemas import ChunkingConfig
from app.rag.ingestion.pdf_loader import PDFLoader
import json

class AIService:
    def __init__(self):
        self.provider = get_llm_provider()
        # RAG components (temporary in-memory wiring)
        self.embedder = OllamaEmbeddingModel()
        self.vector_store = InMemoryVectorStore()
        self.retriever = Retriever(self.embedder, self.vector_store)
        self.rag_pipeline = RAGPipeline(self.retriever)
      
    async def stream_rag_from_pdf(
        self,
        query: str,
        pdf_path: str,
        top_k: int = 5,
    ) -> AsyncGenerator[str, None]:
        """
        Stream LLM response for PDF-based RAG.
        """
        loader = PDFLoader()
        pages = loader.load(pdf_path)

        chunk_config = ChunkingConfig(strategy="paragraph")

        chunks = []
        metadatas = []

        for page in pages:
            if not page["text"]:
                continue

            page_chunks = chunk_text(page["text"], chunk_config)

            for chunk in page_chunks:
                chunks.append(chunk)
                metadatas.append({
                    "page": page["page"],
                    "source": pdf_path,
                })

        embeddings = await self.embedder.embed(chunks)
        self.vector_store.add(embeddings, chunks, metadatas)

        context, sources = await self.rag_pipeline.run(query, top_k=top_k)

        #  Stream ONLY the answer
        async for token in self.provider.stream(
            prompt=query,
            context=context,
        ):
            yield json.dumps({"type": "token","value": token})

        # 🔚 Send sources as final event
        yield json.dumps({
            "type": "sources",
            "value": [
                {
                    "text": doc,
                    "score": score,
                    "metadata": metadata,
                }
                for doc, score, metadata in sources
            ]
        })

        yield json.dumps({ "type": "done" })

  
    async def generate_with_rag_from_pdf(
        self,
        query: str,
        pdf_path: str,
        top_k: int = 5,
    ) -> dict:
        """
        Full RAG flow for PDFs:
        - load PDF page by page
        - paragraph-aware chunking
        - embed + store
        - retrieve
        - generate grounded answer
        """
        loader = PDFLoader()
        pages = loader.load(pdf_path)

        chunk_config = ChunkingConfig(
            strategy="paragraph",
        )

        all_chunks = []
        all_metadatas = []
        
        for page in pages:
            if not page["text"]:
                continue

            chunks = chunk_text(page["text"], chunk_config)

            for chunk in chunks:
                all_chunks.append(chunk)
                all_metadatas.append({
                    "page": page["page"],
                    "source": pdf_path,
                })

        embeddings = await self.embedder.embed(all_chunks)
        self.vector_store.add(embeddings, all_chunks, all_metadatas)

        context, sources = await self.rag_pipeline.run(
            query,
            top_k=top_k,
        )

        answer = await self.provider.generate(
            prompt=query,
            context=context,
        )

        return {
            "answer": answer,
            "sources": sources,
        }

    async def generate_with_rag(
        self,
        query: str,
        documents: str,
        top_k: int = 5,
    ) -> dict:
        """
        Full RAG flow:
        - chunk documents
        - embed + store
        - retrieve
        - generate grounded answer
        """
        chunks = chunk_text(
            documents,
            ChunkingConfig(),
        )

        embeddings = await self.embedder.embed(chunks)
        self.vector_store.add(embeddings, chunks)

        context, sources = await self.rag_pipeline.run(query, top_k=top_k)

        answer = await self.provider.generate(
            prompt=query,
            context=context,
        )

        return {
            "answer": answer,
            "sources": sources,
        }

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
