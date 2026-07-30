from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


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

    # Future Pipeline Scaffolding
    GEMINI_API_KEY: str = ""
    MAX_TOKENS_PER_CHUNK: int = 8000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    def get_upload_path(self) -> Path:
        """Returns Path object for upload directory, creating it if it doesn't exist."""
        path = Path(self.UPLOAD_DIRECTORY)
        path.mkdir(parents=True, exist_ok=True)
        return path


settings = Settings()
