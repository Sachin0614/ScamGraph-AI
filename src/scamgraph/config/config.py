"""
ScamGraph AI - Configuration Management
Loads settings from environment variables with defaults.
"""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()


@dataclass
class DatabaseConfig:
    """Database configuration."""
    path: str = os.getenv("DATABASE_PATH", "data/scamgraph.db")

    @property
    def full_path(self) -> Path:
        """Get absolute path to database file."""
        return Path(self.path).resolve()


@dataclass
class AppConfig:
    """Application configuration."""
    name: str = os.getenv("APP_NAME", "ScamGraph AI")
    version: str = os.getenv("APP_VERSION", "1.0.0")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")


@dataclass
class StreamlitConfig:
    """Streamlit server configuration."""
    port: int = int(os.getenv("STREAMLIT_SERVER_PORT", "8501"))
    address: str = os.getenv("STREAMLIT_SERVER_ADDRESS", "localhost")
    theme_base: str = os.getenv("STREAMLIT_THEME_BASE", "dark")


@dataclass
class SecurityConfig:
    """Security configuration."""
    secret_key: str = os.getenv("SECRET_KEY", "dev-secret-change-me")
    session_timeout_minutes: int = int(os.getenv("SESSION_TIMEOUT_MINUTES", "60"))


@dataclass
class GmailConfig:
    """Gmail API configuration (for future integration)."""
    client_id: str | None = os.getenv("GMAIL_CLIENT_ID")
    client_secret: str | None = os.getenv("GMAIL_CLIENT_SECRET")
    redirect_uri: str | None = os.getenv("GMAIL_REDIRECT_URI")

    @property
    def is_configured(self) -> bool:
        """Check if Gmail credentials are configured."""
        return all([self.client_id, self.client_secret, self.redirect_uri])


@dataclass
class AIConfig:
    """AI/ML model configuration (for future integration)."""
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    anthropic_api_key: str | None = os.getenv("ANTHROPIC_API_KEY")


@dataclass
class TinyFishConfig:
    """TinyFish research API configuration (for future integration)."""
    api_key: str | None = os.getenv("TINYFISH_API_KEY")


@dataclass
class Config:
    """Main configuration container."""
    app: AppConfig
    database: DatabaseConfig
    streamlit: StreamlitConfig
    security: SecurityConfig
    gmail: GmailConfig
    ai: AIConfig
    tinyfish: TinyFishConfig

    @classmethod
    def load(cls) -> "Config":
        """Load configuration from environment."""
        return cls(
            app=AppConfig(),
            database=DatabaseConfig(),
            streamlit=StreamlitConfig(),
            security=SecurityConfig(),
            gmail=GmailConfig(),
            ai=AIConfig(),
            tinyfish=TinyFishConfig(),
        )


# Global config instance
config = Config.load()