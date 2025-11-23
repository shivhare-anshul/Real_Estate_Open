"""
Application Settings Configuration
Loads settings from environment variables
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Unstructured.io (open source, no API key needed)
    
    # Database Configuration
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://user:password@localhost:5432/real_estate_db"
    )
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "real_estate_db")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "user")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "password")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", "5432"))
    
    # ChromaDB Configuration
    CHROMA_DB_PATH: str = os.getenv("CHROMA_DB_PATH", "./chroma_db")
    CHROMA_COLLECTION_NAME: str = os.getenv("CHROMA_COLLECTION_NAME", "real_estate_documents")
    
    # LLM Configuration
    # API keys should be set in .env file (never hardcode in source code)
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # Django Configuration
    SECRET_KEY: str = os.getenv("SECRET_KEY", "django-insecure-change-in-production")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    ALLOWED_HOSTS: str = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1")
    
    @property
    def allowed_hosts_list(self) -> list:
        """Get ALLOWED_HOSTS as a list"""
        return [h.strip() for h in self.ALLOWED_HOSTS.split(",")]
    
    # Logging Configuration
    ENABLE_LOGGING: bool = os.getenv("ENABLE_LOGGING", "True").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE_PATH: str = os.getenv("LOG_FILE_PATH", "./logs/app.log")
    
    # Prefect Configuration
    PREFECT_API_URL: str = os.getenv("PREFECT_API_URL", "http://localhost:4200/api")
    PREFECT_API_KEY: Optional[str] = os.getenv("PREFECT_API_KEY", None)
    
    # Application Configuration
    PDF_DIRECTORY: str = os.getenv("PDF_DIRECTORY", "./Data")
    PARSED_OUTPUT_DIR: str = os.getenv("PARSED_OUTPUT_DIR", "./parsed_outputs")
    MAX_WORKERS: int = int(os.getenv("MAX_WORKERS", "4"))
    
    # Base directory
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Global settings instance
settings = Settings()

