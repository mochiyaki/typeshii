from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # MongoDB
    mongodb_uri: str = "mongodb://localhost:27017"
    database_name: str = "typeshii"
    
    # Grok (xAI) API
    grok_api_key: str = ""
    grok_model: str = "grok-2-latest"
    grok_base_url: str = "https://api.x.ai/v1"
    
    # Environment
    environment: str = "development"
    debug: bool = False
    
    # Logging
    log_level: str = "info"
    
    # API
    api_prefix: str = "/api/v1"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
