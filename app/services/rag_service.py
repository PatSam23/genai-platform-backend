import json
import os
import uuid
from app.utils.hash import hash_text
from typing import AsyncGenerator
from app.rag.pipeline import RAGPipeline
from app.rag.retriever import Retriever
from app.rag.embeddings import OllamaEmbeddingModel
from app.rag.vector_store import InMemoryVectorStore, ChromaVectorStore
from app.rag.chunking import chunk_text
from app.rag.schemas import ChunkingConfig
from app.rag.ingestion.pdf_loader import PDFLoader
from app.core.config import settings
from app.providers.factory import get_llm_provider


class RAGService:
    def __init__(self):
        self.provider = get_llm_provider()
        self.embedder = OllamaEmbeddingModel()

        if settings.VECTOR_STORE_TYPE == "chroma":
            self.vector_store = ChromaVectorStore(
                persist_dir=settings.VECTOR_STORE_PATH
            )
        else:
            self.vector_store = InMemoryVectorStore()

        self.retriever = Retriever(self.embedder, self.vector_store)
        self.pipeline = RAGPipeline(self.retriever)

    async def generate_from_existing_store(self, query: str, top_k: int = 5):
        context, sources = await self.pipeline.run(query, top_k)
        answer = await self.provider.generate(prompt=query, context=context)
        return {"answer": answer, "sources": sources}

    async def stream_from_pdf(
        self,
        query: str,
        pdf_path: str,
        top_k: int = 5,
    ) -> AsyncGenerator[str, None]:
        loader = PDFLoader()
        pages = loader.load(pdf_path)

        chunk_cfg = ChunkingConfig(strategy="paragraph")

        chunks, metas = [], []
        for page in pages:
            if not page.get("text"):
                continue
            for c in chunk_text(page["text"], chunk_cfg):
                c = c.strip()
                if not c:
                    continue
                chunks.append(c)
                metas.append({
                    "document_name": os.path.basename(pdf_path),
                    "page": page["page"],
                    "type": "pdf",
                })


        if not chunks:
            yield json.dumps({"type": "error", "message": "No content"})
            yield json.dumps({"type": "done"})
            return

        embeds = await self.embedder.embed(chunks)
        self.vector_store.add(embeds, chunks, metas)

        context, sources = await self.pipeline.run(query, top_k)

        async for token in self.provider.stream(prompt=query, context=context):
            yield json.dumps({"type": "token", "value": token})

        yield json.dumps({
            "type": "sources",
            "value": [
                {"text": d, "score": s, "metadata": m}
                for d, s, m in sources
            ],
        })
        yield json.dumps({"type": "done"})

    async def ingest_pdf(self, pdf_path: str) -> dict:
        loader = PDFLoader()
        pages = loader.load(pdf_path)

        chunk_cfg = ChunkingConfig(strategy="paragraph")

        document_id = str(uuid.uuid4())
        document_name = os.path.basename(pdf_path)

        chunks = []
        metadatas = []
        skipped = 0

        for page in pages:
            if not page.get("text"):
                continue

            page_chunks = chunk_text(page["text"], chunk_cfg)

            for chunk in page_chunks:
                chunk = chunk.strip()
                if not chunk:
                    continue

                content_hash = hash_text(chunk)

                # 🔍 Deduplication check
                if isinstance(self.vector_store, ChromaVectorStore):
                    if self.vector_store.exists_by_hash(content_hash):
                        skipped += 1
                        continue

                chunks.append(chunk)
                metadatas.append({
                    "content_hash": content_hash,
                    "document_id": document_id,
                    "document_name": document_name,
                    "page": page["page"],
                    "type": "pdf",
                })

        if not chunks:
            return {
                "status": "skipped",
                "reason": "All chunks already exist",
                "chunks_ingested": 0,
                "chunks_skipped": skipped,
            }

        embeddings = await self.embedder.embed(chunks)

        self.vector_store.add(
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas,
        )

        return {
            "status": "success",
            "document_id": document_id,
            "chunks_ingested": len(chunks),
            "chunks_skipped": skipped,
        }
