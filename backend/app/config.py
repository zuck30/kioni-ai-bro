from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, List
import os
from pathlib import Path

# Root directory of the project
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = ROOT_DIR / ".env"

class Settings(BaseSettings):
    # Model configuration for Pydantic V2
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding='utf-8',
        extra='ignore'  # This prevents crashes if .env has extra variables
    )

    APP_NAME: str = "KIONI AI Bro"
    DEBUG: bool = False
    VERSION: str = "1.0.0"
    
    # App Settings (Matching your .env)
    LOG_LEVEL: str = "info"
    REDIS_URL: Optional[str] = "redis://localhost:6379/0"
    
    # API Keys (Free tier)
    HUGGINGFACE_TOKEN: Optional[str] = None
    OPENROUTER_API_KEY: Optional[str] = None
    
    # AI Models
    TEXT_MODEL_PRIMARY: str = "mistralai/Mistral-7B-Instruct-v0.3"
    TEXT_MODEL_FALLBACK: str = "HuggingFaceH4/zephyr-7b-beta"
    WHISPER_MODEL: str = "base"
    VISION_MODEL: str = "vikhyatk/moondream2"
    TTS_MODEL: str = "tts_models/multilingual/multi-dataset/xtts_v2"
    
    # Swahili-specific
    SWAHILI_ROBERTA: str = "akiraindinesh/swahili-roberta"
    SHENG_DETECTION: bool = True
    
    # ChromaDB
    CHROMA_PERSIST_DIR: str = "./chroma_db"
    COLLECTION_NAME: str = "kioni_memory"
    
    # WebSocket
    WS_HEARTBEAT_INTERVAL: int = 30
    
    # Personality
    DEFAULT_PERSONALITY: dict = {
        "urafiki": 80,
        "ucheshi": 60,
        "hekima": 70,
        "msaada": 90,
        "mode": "rafiki"
    }
    
    # Audio
    MAX_AUDIO_SIZE: int = 10 * 1024 * 1024
    SUPPORTED_AUDIO_FORMATS: List[str] = ["wav", "mp3", "webm", "ogg"]
    
    # Vision
    CAMERA_FRAME_INTERVAL: float = 5.0
    VISION_CONFIDENCE_THRESHOLD: float = 0.6

settings = Settings()