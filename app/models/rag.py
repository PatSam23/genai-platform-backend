from pydantic import BaseModel
from typing import List, Dict, Any


class RAGSource(BaseModel):
    text: str
    score: float
    metadata: Dict[str, Any]


class RAGResponse(BaseModel):
    answer: str
    sources: List[RAGSource]
