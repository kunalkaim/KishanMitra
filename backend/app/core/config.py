import os
from typing import List, Optional
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class Settings(BaseSettings):
    PROJECT_NAME: str = "KisanMitra Decision Intelligence API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Security & JWT
    SECRET_KEY: str = "kisanmitra_super_secret_jwt_key_2026_agriculture_decision_support"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours for seamless farmer UX
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Database configuration (PostgreSQL or SQLite fallback)
    # Default SQLite for local standalone development, easily overridden by .env for Postgres
    DATABASE_URL: str = "sqlite:///./kisanmitra.db"

    @field_validator("DATABASE_URL", mode="after")
    @classmethod
    def resolve_sqlite_url(cls, v: str) -> str:
        if v.startswith("sqlite:///./"):
            rel_path = v.replace("sqlite:///./", "")
            abs_path = os.path.join(ROOT_DIR, rel_path).replace("\\", "/")
            return f"sqlite:///{abs_path}"
        return v
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "*"
    ]
    
    # Agricultural Domain Settings
    DEFAULT_STATE: str = "Uttarakhand"
    STORAGE_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "storage")
    
    # RAG & Gemini LLM Settings
    GEMINI_API_KEY: Optional[str] = None
    RAG_LLM_PROVIDER: str = "gemini"
    RAG_LLM_MODEL: str = "gemini-3.5-flash-lite"
    RAG_TOP_K: int = 3
    RAG_MAX_TOKENS: int = 850
    RAG_TEMPERATURE: float = 0.2
    
    model_config = SettingsConfigDict(
        env_file=(
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), ".env"),
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env"),
            ".env"
        ),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow"
    )


settings = Settings()
