from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    LLM_PROVIDER: str = "ollama"
    OLLAMA_MODEL: str = "llama3"
    OPENAI_API_KEY: str | None = None

    class Config:
        env_file = ".env"

settings = Settings()
