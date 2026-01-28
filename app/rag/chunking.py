from typing import List
from app.rag.schemas import ChunkingConfig


def chunk_text(text: str, config: ChunkingConfig) -> List[str]:
    """
    Split text into overlapping chunks.
    """
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
