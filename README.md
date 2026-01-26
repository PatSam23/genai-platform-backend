# GenAI Project Backend

A concise, production-oriented backend for generative-AI services providing chat, retrieval-augmented generation (RAG), and multi-provider model integrations.

## Features
- REST API (v1) with chat, health, and RAG endpoints
- Provider integrations: OpenAI, Hugging Face, Ollama, Bedrock (extensible)
- RAG pipeline: document loader, chunker, vector store, retrieval service
- Simple configuration and logging modules
- Modular design for testing and extensions

## Quickstart
1. Create a virtual environment and install dependencies:
    ```
    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```
2. Configure environment variables (examples):
    - OPENAI_API_KEY
    - HUGGINGFACE_API_KEY
    - AWS credentials for Bedrock (if used)

3. Run the app:
    ```
    uvicorn main:app --reload
    ```

## Project layout
- main.py — application entry
- api/v1 — HTTP endpoints (chat.py, health.py, rag.py)
- models/providers — model provider implementations and factory
- rag — loader, chunker, vectorstore, service
- services — higher-level AI orchestration
- core — configuration and logging

## API (v1)
- GET /api/v1/health — service status
- POST /api/v1/chat — chat interactions (provider-agnostic)
- POST /api/v1/rag — retrieval-augmented generation requests

Refer to the API docstrings and handler functions for request/response shapes.

## Contributing
Fork, create a feature branch, add tests, and submit a PR. Keep changes small and focused.

## License
Specify a license in LICENSE (e.g., MIT).
