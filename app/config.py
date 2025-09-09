import os
from typing import Optional

class Settings:
    # MongoDB Configuration
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "banking_voice_app")
    COLLECTION_NAME: str = os.getenv("COLLECTION_NAME", "voice_actions")
    
    # Audio Configuration
    TEMP_AUDIO_DIR: str = os.getenv("TEMP_AUDIO_DIR", "temp_audio")
    MAX_AUDIO_FILE_SIZE: int = int(os.getenv("MAX_AUDIO_FILE_SIZE", "10485760"))  # 10MB
    AUDIO_FORMAT: str = "wav"
    
    # API Configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # CORS Configuration
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ]

settings = Settings()