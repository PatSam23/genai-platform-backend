from fastapi import APIRouter, UploadFile, File, Form
from tempfile import NamedTemporaryFile
import shutil
from fastapi.responses import StreamingResponse

from app.services.rag_service import RAGService

router = APIRouter(tags=["RAG"])
rag_service = RAGService()


# ---------------------------------------------------------
# QUERY EXISTING VECTOR STORE (NON-PDF)
# ---------------------------------------------------------
@router.post("/rag/query")
async def rag_query_only(
    query: str = Form(...),
    top_k: int = 5,
):
    return await rag_service.generate_from_existing_store(
        query=query,
        top_k=top_k,
    )


# ---------------------------------------------------------
# STREAMING PDF RAG (SSE)
# ---------------------------------------------------------
@router.post("/rag/pdf/stream")
async def rag_pdf_stream(
    query: str = Form(...),
    file: UploadFile = File(...),
    top_k: int = Form(5),
):
    with NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        shutil.copyfileobj(file.file, tmp)
        pdf_path = tmp.name

    async def event_generator():
        async for chunk in rag_service.stream_from_pdf(
            query=query,
            pdf_path=pdf_path,
            top_k=top_k,
        ):
            yield f"data: {chunk}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
    )
# ---------------------------------------------------------
# INGEST PDF INTO VECTOR STORE (NO QUERY)
# ---------------------------------------------------------
@router.post("/rag/ingest/pdf")
async def ingest_pdf(
    file: UploadFile = File(...),
):
    with NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        shutil.copyfileobj(file.file, tmp)
        pdf_path = tmp.name

    result = await rag_service.ingest_pdf(
        pdf_path=pdf_path,
    )

    return result

# ---------------------------------------------------------
# NON-STREAMING PDF RAG (REST)
# ---------------------------------------------------------
@router.post("/rag/pdf")
async def rag_from_pdf(
    query: str = Form(...),
    file: UploadFile = File(...),
    top_k: int = Form(5),
):
    with NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        shutil.copyfileobj(file.file, tmp)
        pdf_path = tmp.name

    result = await rag_service.generate_from_existing_store(
        query=query,
        top_k=top_k,
    )

    return {
        "answer": result["answer"],
        "sources": [
            {
                "text": doc,
                "score": score,
                "metadata": metadata,
            }
            for doc, score, metadata in result["sources"]
        ],
    }
