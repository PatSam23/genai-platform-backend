from fastapi import APIRouter, UploadFile, File, Form
from tempfile import NamedTemporaryFile
import shutil
from fastapi.responses import StreamingResponse
from app.services.ai_service import AIService

router = APIRouter(tags=["RAG"])

ai_service = AIService()

@router.post("/rag/query")
async def rag_query_only(
    query: str = Form(...),
    top_k: int = 5,
):
    result = await ai_service.generate_with_rag_from_existing_store(
        query=query,
        top_k=top_k,
    )
    return result

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
        async for chunk in ai_service.stream_rag_from_pdf(
            query=query,
            pdf_path=pdf_path,
            top_k=top_k,
        ):
            yield f"data: {chunk}\n\n"

        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
    )
    
@router.post("/rag/pdf")
async def rag_from_pdf(
    query: str = Form(...),
    file: UploadFile = File(...),
    top_k: int = Form(5),
):
    """
    RAG over uploaded PDF with source attribution.
    """
    # Save uploaded PDF to a temp file
    with NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        shutil.copyfileobj(file.file, tmp)
        pdf_path = tmp.name

    result = await ai_service.generate_with_rag_from_pdf(
        query=query,
        pdf_path=pdf_path,
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
