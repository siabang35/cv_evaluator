from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_SERVICE_KEY: str
    
    # API Keys
    GROQ_API_KEY: str
    OPENAI_API_KEY: Optional[str] = None  # biar gak error
    
    # Redis Cloud
    REDIS_PASSWORD: str
    REDIS_HOST: str = "redis-10110.c245.us-east-1-3.ec2.redns.redis-cloud.com"
    REDIS_PORT: int = 10110

    # Celery
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None

    # RAG configs
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    TOP_K_CHUNKS: int = 5

    # App
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str
    LOG_LEVEL: str = "INFO"
    
    # Storage
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 10485760
    
    # LLM
    LLM_MODEL: str = "llama-3.1-70b-versatile"
    EMBEDDING_MODEL: str = "text-embedding-ada-002"
    LLM_TEMPERATURE: float = 0.3
    MAX_TOKENS: int = 4000
    MAX_RETRIES: int = 3
    RETRY_DELAY: int = 2
    
    GROQ_API_BASE: str = "https://api.groq.com/openai/v1"
    
    # ChromaDB
    CHROMA_PERSIST_DIR: str = "./chroma_db"
    
    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:3001"

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"  # biar kalau masih ada variabel lain gak error

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",")]

    @property
    def redis_url(self) -> str:
        return f"redis://default:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/0"
    
    @property
    def celery_broker_url(self) -> str:
        return self.CELERY_BROKER_URL or self.redis_url
    
    @property
    def celery_result_backend(self) -> str:
        return self.CELERY_RESULT_BACKEND or self.redis_url


settings = Settings()
