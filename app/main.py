from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.v1 import chat, rag, auth, health, chat_history
from fastapi.middleware.cors import CORSMiddleware
from app.core.logging import setup_logger

logger = setup_logger(__name__, log_file="logs/app.log")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application startup complete")
    yield
    logger.info("Application shutting down")


app = FastAPI(
    title="GenAI Platform Backend",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

logger.info("Initializing GenAI Platform Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("CORS middleware configured")

app.include_router(health.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")
app.include_router(rag.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(chat_history.router, prefix="/api/v1")

logger.info("All API routers registered successfully")
