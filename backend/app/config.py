"""Application configuration for SceneSpeak.

Loads configuration from environment variables and `.env` file using Pydantic Settings.
"""

from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """SceneSpeak configuration settings."""
    model_config = SettingsConfigDict(
        env_file=(".env", "backend/.env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Model Provider ("gemini" or "openai")
    vlm_provider: str = "gemini"
    vlm_api_key: str = ""
    vlm_model: str = "gemini-2.0-flash"
    vlm_base_url: Optional[str] = None

    # VLM Generation Parameters (Section 8.3)
    temperature: float = 0.2
    max_tokens: int = 200
    timeout_seconds: float = 15.0
    max_retries: int = 1

    # Security & limits (Section 7.2 & 11.3)
    max_image_bytes: int = 2_000_000  # 2 MB payload cap
    rate_limit_per_min: int = 30

    # Database
    database_url: str = "sqlite:///./scenespeak.db"

    # Server runtime
    host: str = "0.0.0.0"
    port: int = 8000


settings = Settings()
