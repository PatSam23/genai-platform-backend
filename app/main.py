from fastapi import FastAPI
from app.api.v1 import chat, rag, health

app = FastAPI(title="GenAI Platform Backend")

app.include_router(health.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")
app.include_router(rag.router, prefix="/api/v1")
