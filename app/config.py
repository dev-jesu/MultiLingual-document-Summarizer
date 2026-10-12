from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    """
    Application Configuration loaded from environment variables or .env file.
    """
    APP_NAME: str = "Multilingual Legal Document Summarizer"
    DEBUG: bool = False

    # Upload Settings
    MAX_UPLOAD_SIZE: int = 104_857_600  # 100 MB in bytes
    UPLOAD_DIRECTORY: str = "uploads"
    ALLOWED_EXTENSIONS: set[str] = {".pdf", ".docx"}

    # Gemini API Configuration (Free Tier)
    GEMINI_API_KEY: str = ""
    MODEL_NAME: str = "gemini-2.5-flash-lite"

    # Token & Chunking Limits
    MAX_INPUT_TOKENS: int = 6000
    MAX_OUTPUT_TOKENS: int = 1024
    TARGET_SUMMARY_WORDS: int = 500
    CHUNK_OVERLAP: int = 150
    DEFAULT_CHUNK_STRATEGY: str = "merged"
    DEFAULT_MAX_TOKENS: int = 6000
    DEFAULT_CHUNK_OVERLAP: int = 150

    # Retry & Timeout Configuration
    MAX_RETRIES: int = 3
    REQUEST_TIMEOUT: float = 60.0

    # Multilingual Support
    DEFAULT_SOURCE_LANGUAGE: str = "auto"
    DEFAULT_TARGET_LANGUAGE: str = "en"
    SUPPORTED_LANGUAGES: str = "en,ta,hi,te,kn,ml,mr"

    # Export Settings (Stage 7)
    DEFAULT_EXPORT_FORMAT: str = "pdf"
    TEMP_EXPORT_DIRECTORY: str = "temp"
    REPORT_TITLE: str = "District Court e-Services"

    # Local JWT Auth (replaces Supabase Auth)
    JWT_SECRET: str = os.getenv("JWT_SECRET", "ecourt-local-jwt-secret-change-me-in-prod")

    # Supabase Configuration (used only for DB/storage if needed, NOT for auth)
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    SUPABASE_JWT_SECRET: str = os.getenv("SUPABASE_JWT_SECRET", "")
    SUPABASE_JWKS_URL: str = os.getenv("SUPABASE_JWKS_URL", "")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    def get_upload_path(self) -> Path:
        """Returns Path object for upload directory, creating it if it does not exist."""
        path = Path(self.UPLOAD_DIRECTORY)
        path.mkdir(parents=True, exist_ok=True)
        return path

settings = Settings()
