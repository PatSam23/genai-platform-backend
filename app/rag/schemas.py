from pydantic import BaseModel


class ChunkingConfig(BaseModel):
    chunk_size: int = 500
    chunk_overlap: int = 50
