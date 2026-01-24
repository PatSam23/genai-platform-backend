from fastapi import APIRouter

router = APIRouter(tags=["Chat"])

@router.post("/chat")
async def chat_endpoint():
    return {
        "message": "Chat endpoint is alive"
    }
