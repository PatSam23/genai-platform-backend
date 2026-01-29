from pydantic import BaseModel
from typing import Literal

class ChunkingConfig(BaseModel):
    chunk_size: int = 500
    chunk_overlap: int = 50
    strategy: Literal["fixed", "paragraph"] = "fixed"
