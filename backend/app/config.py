import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

# Find backend/.env path reliably
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_ENV_FILE = os.path.join(_BASE_DIR, ".env")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_ENV_FILE if os.path.exists(_ENV_FILE) else ".env",
        extra="ignore"
    )

    # Database - SQLite by default for zero-friction local run
    DATABASE_URL: str = "sqlite:///./nbfc_loan.db"
    
    # Google Gemini Configuration (Primary Provider)
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"
    GEMINI_VISION_MODEL: str = "gemini-2.5-flash"

    # Groq LLM Configuration (Alternative Provider)
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
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
    



@lru_cache()
def get_settings() -> Settings:
    return Settings()
