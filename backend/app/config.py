import os
from pydantic_settings import BaseSettings
from functools import lru_cache

# Find backend/.env path reliably
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_ENV_FILE = os.path.join(_BASE_DIR, ".env")


class Settings(BaseSettings):
    # Database - SQLite by default for zero-friction local run
    DATABASE_URL: str = "sqlite:///./nbfc_loan.db"
    
    # Groq LLM Configuration
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.1-8b-instant"
    GROQ_VISION_MODEL: str = "llama-3.2-11b-vision-preview"
    
    # CORS
    FRONTEND_URL: str = "http://localhost:3000"
    
    # External Credit Bureau API (optional)
    CREDIT_API_URL: str = ""
    CREDIT_API_KEY: str = ""
    
    # Security
    SECRET_KEY: str = "nbfc-loan-chatbot-super-secret-key-2025"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # File Upload
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 10485760  # 10MB
    
    # Mock APIs
    MOCK_CRM_ENABLED: bool = True
    MOCK_CREDIT_BUREAU_ENABLED: bool = True
    
    class Config:
        env_file = _ENV_FILE if os.path.exists(_ENV_FILE) else ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
