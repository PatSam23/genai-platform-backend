from fastapi import APIRouter

router = APIRouter(tags=["RAG"])

@router.post("/rag/query")
async def rag_query():
    return {
        "message": "RAG endpoint is alive"
    }
