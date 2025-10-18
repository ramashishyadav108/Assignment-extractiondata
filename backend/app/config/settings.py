import os
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import model_validator

# Get the backend directory  (where this file's parent/parent/parent is)
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
# Project root directory (parent of backend)
PROJECT_ROOT = BACKEND_DIR.parent


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "PDF Extraction System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Project root for reference
    PROJECT_ROOT: Path = PROJECT_ROOT
    
    # API Keys
    GEMINI_API_KEY: str = ""
    
    # File Upload - these will be set to absolute paths by the validator
    UPLOAD_DIR: Path = Path("examples/sample_pdfs")
    OUTPUT_DIR: Path = Path("examples/output")
    TEMPLATE_DIR: Path = Path("templates")
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS: set = {".pdf"}
    
    # Database (Optional)
    DATABASE_URL: str = ""
    
    # LLM Configuration
    LLM_MODEL: str = "gemini-2.5-flash"  # Stable version of Gemini 2.5 Flash
    LLM_TEMPERATURE: float = 0.1
    LLM_MAX_RETRIES: int = 3
    
    # CORS
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    @model_validator(mode='after')
    def resolve_paths(self):
        """Resolve relative paths to absolute paths based on project root."""
        # Only resolve if they are relative paths
        if not self.UPLOAD_DIR.is_absolute():
            self.UPLOAD_DIR = PROJECT_ROOT / self.UPLOAD_DIR
        if not self.OUTPUT_DIR.is_absolute():
            self.OUTPUT_DIR = PROJECT_ROOT / self.OUTPUT_DIR
        if not self.TEMPLATE_DIR.is_absolute():
            self.TEMPLATE_DIR = PROJECT_ROOT / self.TEMPLATE_DIR
        return self


settings = Settings()

# Ensure directories exist
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
settings.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
(settings.PROJECT_ROOT / "jobs").mkdir(parents=True, exist_ok=True)

