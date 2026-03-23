from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, List
import os
from pathlib import Path

# Find the root directory (where .env is)
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = ROOT_DIR / ".env"

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding='utf-8',
        extra='ignore'
    )

    APP_NAME: str = "KIONI AI Bro"
    DEBUG: bool = False
    VERSION: str = "1.0.0"
    
    LOG_LEVEL: str = "info"
    REDIS_URL: Optional[str] = None
    
    # API Keys
    HUGGINGFACE_TOKEN: Optional[str] = None
    OPENROUTER_API_KEY: Optional[str] = None
    
    # AI Models - These will be loaded from .env
    TEXT_MODEL_PRIMARY: str = "HuggingFaceH4/zephyr-7b-beta"
    TEXT_MODEL_FALLBACK: str = "google/flan-t5-large"
    WHISPER_MODEL: str = "base"
    TTS_MODEL: str = "tts_models/multilingual/multi-dataset/xtts_v2"
    
    SWAHILI_ROBERTA: str = "akiraindinesh/swahili-roberta"
    SHENG_DETECTION: bool = True
    
    CHROMA_PERSIST_DIR: str = "./chroma_db"
    COLLECTION_NAME: str = "kioni_memory"
    WS_HEARTBEAT_INTERVAL: int = 30
    
    DEFAULT_PERSONALITY: dict = {
        "urafiki": 80,
        "ucheshi": 60,
        "hekima": 70,
        "msaada": 90,
        "mode": "rafiki"
    }
    
    MAX_AUDIO_SIZE: int = 10 * 1024 * 1024
    SUPPORTED_AUDIO_FORMATS: List[str] = ["wav", "mp3", "webm", "ogg"]
    CAMERA_FRAME_INTERVAL: float = 5.0
    VISION_CONFIDENCE_THRESHOLD: float = 0.6

settings = Settings()

# Debug info
print(f"📝 Configuration loaded:")
print(f"   Primary Model: {settings.TEXT_MODEL_PRIMARY}")
print(f"   Fallback Model: {settings.TEXT_MODEL_FALLBACK}")
print(f"   HuggingFace Token: {'✅ Loaded' if settings.HUGGINGFACE_TOKEN else '❌ Missing'}")
print(f"   OpenRouter Key: {'✅ Loaded' if settings.OPENROUTER_API_KEY else '❌ Missing'}")