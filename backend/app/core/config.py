"""
Application configuration using Pydantic Settings.
Loads configuration from environment variables.
"""
from typing import List
import json
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Project Info
    PROJECT_NAME: str = "ERP Multi-Tenant API"
    VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    
    # Database
    DATABASE_URL: str = "postgresql://erp_user:erp_password@localhost:5432/erp_db"
    
    # JWT Authentication
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production-please-use-strong-random-key"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # AI Integration
    AI_PROVIDER: str = "claude"  # claude | openai | xai
    AI_API_KEY: str = ""
    
    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8000"
    
    @field_validator('ALLOWED_ORIGINS', mode='after')
    @classmethod
    def parse_allowed_origins(cls, v: str) -> List[str]:
        """
        Parse ALLOWED_ORIGINS from various formats:
        - JSON array: ["http://localhost:3000","https://example.com"]
        - Comma-separated: http://localhost:3000,https://example.com
        - Single string: http://localhost:3000
        """
        # Try to parse as JSON first
        try:
            parsed = json.loads(v)
            if isinstance(parsed, list):
                return parsed
        except (json.JSONDecodeError, TypeError):
            pass
        
        # Handle comma-separated string
        if ',' in v:
            return [origin.strip() for origin in v.split(',') if origin.strip()]
        
        # Handle single string
        if v and v.strip():
            return [v.strip()]
        
        # Fallback to default
        return ["http://localhost:3000", "http://localhost:8000"]
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra='ignore',  # Ignore extra environment variables not defined in Settings
    )


# Create settings instance
settings = Settings()
