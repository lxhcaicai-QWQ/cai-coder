"""
Feishu Bot Configuration
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Bot configuration settings"""

    # Feishu App Settings
    feishu_app_id: str
    feishu_app_secret: str
    feishu_encrypt_key: Optional[str] = None
    feishu_verification_token: str

    # Cai-Coder API Settings
    caicoder_api_url: str = "http://localhost:8000"
    caicoder_model: str = "cai-coder"
    caicoder_stream: bool = False

    # Bot Settings
    bot_name: str = "cai-coder"
    bot_port: int = 8080
    bot_host: str = "0.0.0.0"

    # Conversation Settings
    max_history: int = 10  # Maximum messages to keep in conversation history
    session_ttl: int = 3600  # Session TTL in seconds (1 hour)

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
