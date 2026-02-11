from fastapi import APIRouter, UploadFile, File, Form
from tempfile import NamedTemporaryFile
import shutil
import os
from fastapi.responses import StreamingResponse

from app.services.rag_service import RAGService
from app.core.logging import setup_logger

logger = setup_logger(__name__, log_file="logs/rag.log")
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
    logger.info(f"RAG query request - query: '{query[:100]}...', top_k: {top_k}")
    try:
        result = await rag_service.generate_from_existing_store(
            query=query,
            top_k=top_k,
        )
        logger.info(f"RAG query completed - sources found: {len(result.get('sources', []))}")
        return result
    except Exception as e:
        logger.error(f"Error processing RAG query: {str(e)}", exc_info=True)
        raise


# ---------------------------------------------------------
# STREAMING PDF RAG (SSE)
# ---------------------------------------------------------
@router.post("/rag/pdf/stream")
async def rag_pdf_stream(
    query: str = Form(...),
    file: UploadFile = File(...),
    top_k: int = Form(5),
):
    logger.info(f"PDF streaming RAG request - file: {file.filename}, query: '{query[:100]}...', top_k: {top_k}")
    
    with NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        shutil.copyfileobj(file.file, tmp)
        pdf_path = tmp.name
    
    logger.info(f"PDF saved to temporary path: {pdf_path}")

    async def event_generator():
        try:
            async for chunk in rag_service.stream_from_pdf(
                query=query,
                pdf_path=pdf_path,
                top_k=top_k,
            ):
                yield f"data: {chunk}\n\n"
            logger.info(f"PDF streaming RAG completed for {file.filename}")
        except Exception as e:
            logger.error(f"Error during PDF streaming RAG: {str(e)}", exc_info=True)
        finally:
            # Cleanup temporary file
            try:
                os.unlink(pdf_path)
                logger.debug(f"Temporary PDF file deleted: {pdf_path}")
            except Exception as e:
                logger.warning(f"Failed to delete temporary file {pdf_path}: {str(e)}")

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
    logger.info(f"PDF ingestion request - file: {file.filename}")
    
    with NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        shutil.copyfileobj(file.file, tmp)
        pdf_path = tmp.name
    
    logger.info(f"PDF saved to temporary path for ingestion: {pdf_path}")

    try:
        result = await rag_service.ingest_pdf(
            pdf_path=pdf_path,
        )
        logger.info(f"PDF ingestion completed - file: {file.filename}, chunks: {result.get('chunks_added', 'N/A')}")
        return result
    except Exception as e:
        logger.error(f"Error ingesting PDF {file.filename}: {str(e)}", exc_info=True)
        raise
    finally:
        # Cleanup temporary file
        try:
            os.unlink(pdf_path)
            logger.debug(f"Temporary PDF file deleted: {pdf_path}")
        except Exception as e:
            logger.warning(f"Failed to delete temporary file {pdf_path}: {str(e)}")

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
