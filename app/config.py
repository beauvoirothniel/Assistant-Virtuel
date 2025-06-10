import os
from typing import Optional
from pydantic import BaseSettings

class Settings(BaseSettings):
    # API Keys
    OPENAI_API_KEY: str
    
    # Base de données
    DATABASE_URL: str = "sqlite:///./salon.db"
    
    # Services externes
    REDIS_URL: str = "redis://localhost:6379"
    
    # Configuration audio/vidéo
    VOICE_LANGUAGE: str = "fr-FR"
    VOICE_RATE: int = 150
    VOICE_VOLUME: float = 0.9
    CAMERA_INDEX: int = 0
    
    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = False
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    
    # Sécurité
    SECRET_KEY: str
    ALLOWED_HOSTS: list = ["*"]
    
    class Config:
        env_file = ".env"

settings = Settings()