"""
ScamGraph AI - Application Configuration
Handles environment-driven settings, API keys, thresholds, and safety policies.
"""

from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    # App
    PROJECT_NAME: str = "ScamGraph AI"
    VERSION: str = "2.0.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str = f"sqlite:///{BASE_DIR}/data/scamgraph_v2.db"
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]
    
    # TinyFish Intelligence Service
    TINYFISH_API_KEY: Optional[str] = None
    TINYFISH_API_BASE_URL: str = "https://api.tinyfish.io/v1"
    TINYFISH_ENABLED: bool = False
    TINYFISH_TIMEOUT_SECONDS: int = 10
    TINYFISH_MAX_RETRIES: int = 2
    
    # AI LLM Provider Configuration (Optional)
    OPENAI_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    AI_MODEL_NAME: str = "rule-engine-v2"
    
    # Security & SSRF Protection
    ALLOWED_DOMAINS: List[str] = []
    MAX_URL_RESPONSE_SIZE_BYTES: int = 1_048_576  # 1MB limit for untrusted external fetching
    REQUEST_TIMEOUT_SECONDS: int = 8
    
    # Similarity detection thresholds
    TEXT_SIMILARITY_THRESHOLD: float = 0.55
    EXACT_INDICATOR_CONFIDENCE: float = 0.95
    SIMILAR_TEXT_CONFIDENCE: float = 0.65

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
