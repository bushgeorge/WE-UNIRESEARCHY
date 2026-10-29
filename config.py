"""
Application configuration settings
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "WE UNIRESEARCHITY"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database
    DATABASE_URL: str = "sqlite:///./database/research.db"
    
    # File upload
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 20 * 1024 * 1024  # 20MB
    ALLOWED_EXTENSIONS: set = {".pdf"}
    
    # Security
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD_HASH: str = "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"  # bcrypt hash for "admin123"
    SECRET_KEY: str = "your-secret-key-change-in-production"
    
    # CORS
    CORS_ORIGINS: list = ["*"]
    
    # Email (for future use)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[int] = None
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    FROM_EMAIL: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Create settings instance
settings = Settings()

# Ensure upload directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs("database", exist_ok=True)