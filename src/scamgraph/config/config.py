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

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent


@dataclass
class DatabaseConfig:
    """Database configuration."""
    path: str = os.getenv("DATABASE_PATH", "data/scamgraph.db")

    @property
    def full_path(self) -> Path:
        """Get absolute path to database file securely anchored to project root."""
        p = Path(self.path)
        if not p.is_absolute():
            return (PROJECT_ROOT / p).resolve()
        return p.resolve()


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
        return bool(self.client_id and self.client_secret)


class Config:
    """Main configuration container."""

    def __init__(self) -> None:
        self.database = DatabaseConfig()
        self.app = AppConfig()
        self.streamlit = StreamlitConfig()
        self.security = SecurityConfig()
        self.gmail = GmailConfig()

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.app.debug

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return not self.app.debug


# Global configuration instance
config = Config()


def get_config() -> Config:
    """Get the global configuration instance."""
    return config
