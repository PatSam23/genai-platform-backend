from typing import List
from app.rag.schemas import ChunkingConfig
import re

def chunk_text(text: str, config: ChunkingConfig) -> List[str]:
    if config.strategy == "paragraph":
        return _chunk_by_paragraph(text, config)

    # default fallback
    return _chunk_fixed(text, config)

def _chunk_fixed(text: str, config: ChunkingConfig) -> List[str]:
    chunks = []
    start = 0
    length = len(text)

    while start < length:
        end = start + config.chunk_size
        chunk = text[start:end]
        chunks.append(chunk)

        start = end - config.chunk_overlap
        if start < 0:
            start = 0

    return chunks


def _chunk_by_paragraph(text: str, config: ChunkingConfig) -> List[str]:
    paragraphs = [
        p.strip()
        for p in re.split(r"\n\s*\n+", text)
        if p.strip()
    ]

    chunks: List[str] = []
    current_chunk = ""

    for paragraph in paragraphs:
        # If adding this paragraph exceeds chunk size → flush
        if len(current_chunk) + len(paragraph) > config.chunk_size:
            chunks.append(current_chunk.strip())
            current_chunk = paragraph + "\n\n"
        else:
            current_chunk += paragraph + "\n\n"

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks
