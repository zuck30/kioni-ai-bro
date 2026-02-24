from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime
from enum import Enum

class Language(str, Enum):
    SWAHILI = "sw"
    ENGLISH = "en"
    SHENG = "sheng"
    MIXED = "mixed"

class Mood(str, Enum):
    POA = "poa"           # Cool/chill
    SAFI = "safi"         # Good/okay
    MZITO = "mzito"       # Serious
    MCHEKESHAJI = "mchekeshaji"  # Funny
    MSHAURI = "mshauri"   # Advisor
    SHUGHULI = "shughuli" # Busy

class MessageType(str, Enum):
    TEXT = "text"
    VOICE = "voice"
    IMAGE = "image"
    SYSTEM = "system"

class ChatMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(datetime.now().timestamp()))
    role: Literal["user", "kioni", "system"]
    content: str
    type: MessageType = MessageType.TEXT
    language: Language = Language.MIXED
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Optional[Dict[str, Any]] = None
    emotion_score: Optional[float] = None  # -1 to 1

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    context: Optional[List[ChatMessage]] = []
    mood_override: Optional[Mood] = None

class ChatResponse(BaseModel):
    message: ChatMessage
    suggested_responses: Optional[List[str]] = None
    personality_state: Dict[str, Any]
    detected_language: Language

class VoiceRequest(BaseModel):
    audio_base64: str
    format: str = "webm"
    session_id: Optional[str] = None

class VisionRequest(BaseModel):
    image_base64: str
    context: Optional[str] = None  # Previous conversation context

class VisionResponse(BaseModel):
    description: str
    objects: List[Dict[str, Any]]
    swahili_context: str  # Culturally-aware description
    mood_suggestion: Optional[Mood]

class HaliState(BaseModel):
    current_mood: Mood
    urafiki: int = Field(ge=0, le=100)
    ucheshi: int = Field(ge=0, le=100)
    hekima: int = Field(ge=0, le=100)
    msaada: int = Field(ge=0, le=100)
    current_greeting: str
    time_of_day: str
    active_sessions: int

class PersonalityUpdate(BaseModel):
    urafiki: Optional[int] = Field(None, ge=0, le=100)
    ucheshi: Optional[int] = Field(None, ge=0, le=100)
    hekima: Optional[int] = Field(None, ge=0, le=100)
    msaada: Optional[int] = Field(None, ge=0, le=100)
    mode: Optional[Mood] = None

class WebSocketMessage(BaseModel):
    type: Literal["chat", "typing", "vision", "voice", "system", "error"]
    payload: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.now)