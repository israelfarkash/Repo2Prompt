"""Application configuration using Pydantic Settings.

Loads configuration from environment variables and .env file.
All settings are validated at startup using Pydantic v2.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support.

    Attributes:
        DATABASE_URL: PostgreSQL connection string using asyncpg driver.
        GEMINI_API_KEY: API key for Google Gemini AI service.
        AI_PROVIDER: The AI provider to use for analysis (default: gemini).
        AI_MODEL: The specific AI model to use (default: gemini-2.5-flash).
        GITHUB_TOKEN: Optional GitHub personal access token for private repos.
        MAX_REPO_SIZE_MB: Maximum allowed repository size in megabytes.
        ANALYSIS_TIMEOUT_SECONDS: Maximum time allowed for a single analysis run.
        CLONE_DIR: Temporary directory for cloning repositories.
        BACKEND_CORS_ORIGINS: List of allowed CORS origins for the frontend.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    DATABASE_URL: str = "sqlite+aiosqlite:///./ai_reverse_engineer.db"
    GEMINI_API_KEY: str = ""
    AI_PROVIDER: str = "gemini"
    AI_MODEL: str = "gemini-2.5-flash"
    GITHUB_TOKEN: str = ""
    MAX_REPO_SIZE_MB: int = 100
    ANALYSIS_TIMEOUT_SECONDS: int = 600
    CLONE_DIR: str = "/tmp/repos"
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000"]


settings = Settings()
