from typing import AsyncGenerator
import json

from app.providers.factory import get_llm_provider
from app.rag.pipeline import RAGPipeline
from app.rag.retriever import Retriever
from app.rag.embeddings import OllamaEmbeddingModel
from app.rag.vector_store import InMemoryVectorStore, ChromaVectorStore
from app.rag.chunking import chunk_text
from app.rag.schemas import ChunkingConfig
from app.rag.ingestion.pdf_loader import PDFLoader
from app.core.config import settings


class AIService:
    def __init__(self):
        self.provider = get_llm_provider()

        # RAG components
        self.embedder = OllamaEmbeddingModel()

        if settings.VECTOR_STORE_TYPE == "chroma":
            self.vector_store = ChromaVectorStore(
                persist_dir=settings.VECTOR_STORE_PATH
            )
        else:
            self.vector_store = InMemoryVectorStore()

        self.retriever = Retriever(self.embedder, self.vector_store)
        self.rag_pipeline = RAGPipeline(self.retriever)


    async def generate_with_rag_from_existing_store(
        self,
        query: str,
        top_k: int = 5,
    ) -> dict:
        context, sources = await self.rag_pipeline.run(query, top_k=top_k)

        answer = await self.provider.generate(
            prompt=query,
            context=context,
        )

        return {
            "answer": answer,
            "sources": sources,
        }

    # ---------------------------------------------------------
    # STREAMING PDF RAG
    # ---------------------------------------------------------
    async def stream_rag_from_pdf(
        self,
        query: str,
        pdf_path: str,
        top_k: int = 5,
    ) -> AsyncGenerator[str, None]:
        loader = PDFLoader()
        pages = loader.load(pdf_path)

        chunk_config = ChunkingConfig(strategy="paragraph")

        clean_chunks: list[str] = []
        clean_metadatas: list[dict] = []

        for page in pages:
            if not page.get("text"):
                continue

            page_chunks = chunk_text(page["text"], chunk_config)

            for chunk in page_chunks:
                chunk = chunk.strip()
                if not chunk:
                    continue  # 🚫 critical: skip empty chunks

                clean_chunks.append(chunk)
                clean_metadatas.append({
                    "page": page["page"],
                    "source": pdf_path,
                })

        if not clean_chunks:
            yield json.dumps({
                "type": "error",
                "message": "No valid text chunks extracted from PDF."
            })
            yield json.dumps({"type": "done"})
            return

        embeddings = await self.embedder.embed(clean_chunks)
        self.vector_store.add(embeddings, clean_chunks, clean_metadatas)

        context, sources = await self.rag_pipeline.run(query, top_k=top_k)

        # 🔹 Stream answer tokens
        async for token in self.provider.stream(
            prompt=query,
            context=context,
        ):
            yield json.dumps({
                "type": "token",
                "value": token,
            })

        # 🔹 Send sources
        yield json.dumps({
            "type": "sources",
            "value": [
                {
                    "text": doc,
                    "score": score,
                    "metadata": metadata,
                }
                for doc, score, metadata in sources
            ],
        })

        yield json.dumps({"type": "done"})

    # ---------------------------------------------------------
    # NON-STREAMING PDF RAG
    # ---------------------------------------------------------
    async def generate_with_rag_from_pdf(
        self,
        query: str,
        pdf_path: str,
        top_k: int = 5,
    ) -> dict:
        loader = PDFLoader()
        pages = loader.load(pdf_path)

        chunk_config = ChunkingConfig(strategy="paragraph")

        clean_chunks: list[str] = []
        clean_metadatas: list[dict] = []

        for page in pages:
            if not page.get("text"):
                continue

            chunks = chunk_text(page["text"], chunk_config)

            for chunk in chunks:
                chunk = chunk.strip()
                if not chunk:
                    continue  # 🚫 critical: skip empty chunks

                clean_chunks.append(chunk)
                clean_metadatas.append({
                    "page": page["page"],
                    "source": pdf_path,
                })

        if not clean_chunks:
            return {
                "answer": "No usable content found in the PDF.",
                "sources": [],
            }

        embeddings = await self.embedder.embed(clean_chunks)
        self.vector_store.add(embeddings, clean_chunks, clean_metadatas)

        context, sources = await self.rag_pipeline.run(query, top_k=top_k)

        answer = await self.provider.generate(
            prompt=query,
            context=context,
        )

        return {
            "answer": answer,
            "sources": sources,
        }

    # ---------------------------------------------------------
    # TEXT-BASED RAG (NON-PDF)
    # ---------------------------------------------------------
    async def generate_with_rag(
        self,
        query: str,
        documents: str,
        top_k: int = 5,
    ) -> dict:
        chunks = chunk_text(
            documents,
            ChunkingConfig(),
        )

        clean_chunks = [c.strip() for c in chunks if c.strip()]

        if not clean_chunks:
            return {
                "answer": "No usable content provided.",
                "sources": [],
            }

        metadatas = [{} for _ in clean_chunks]

        embeddings = await self.embedder.embed(clean_chunks)
        self.vector_store.add(embeddings, clean_chunks, metadatas)

        context, sources = await self.rag_pipeline.run(query, top_k=top_k)

        answer = await self.provider.generate(
            prompt=query,
            context=context,
        )

        return {
            "answer": answer,
            "sources": sources,
        }

    # ---------------------------------------------------------
    # BASIC CHAT (NON-RAG)
    # ---------------------------------------------------------
    async def generate_response(
        self,
        prompt: str,
        context: str | None = None,
    ) -> str:
        final_prompt = self._build_prompt(prompt)
        return await self.provider.generate(final_prompt, context)

    async def stream_response(
        self,
        prompt: str,
        context: str | None = None,
    ) -> AsyncGenerator[str, None]:
        final_prompt = self._build_prompt(prompt)
        async for token in self.provider.stream(final_prompt, context):
            yield token

    def _build_prompt(self, prompt: str) -> str:
        return f"You are a helpful AI assistant.\nUser: {prompt}\nAssistant:"
