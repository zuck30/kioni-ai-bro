import io
import base64
import tempfile
import os
from typing import Optional, Tuple
try:
    import whisper
    HAS_WHISPER = True
except ImportError:
    HAS_WHISPER = False

try:
    from TTS.api import TTS
    HAS_TTS = True
except ImportError:
    HAS_TTS = False
    print("Warning: TTS package not found. Voice responses will be disabled.")
from ...config import settings

class SpeechProcessor:
    def __init__(self):
        self.whisper_model = None
        self.tts_model = None
        # Removed immediate call to _load_models() to prevent startup crashes
        
    def _load_models(self):
        """Lazy load models with error handling"""
        if self.whisper_model is None:
            if not HAS_WHISPER:
                print("Error: Whisper package not found.")
            else:
                try:
                    print("Loading Whisper model...")
                    self.whisper_model = whisper.load_model(settings.WHISPER_MODEL)
                except Exception as e:
                    print(f"Error loading Whisper model: {e}")
                    self.whisper_model = None
        
        if self.tts_model is None and HAS_TTS:
            try:
                print("Loading TTS model...")
                # Using Coqui TTS with XTTS v2 for multilingual support
                self.tts_model = TTS(settings.TTS_MODEL)
            except Exception as e:
                print(f"Error loading TTS model: {e}")
                self.tts_model = None
    
    async def speech_to_text(
        self, 
        audio_bytes: bytes, 
        language: Optional[str] = None
    ) -> Tuple[str, str]:
        """
        Convert speech to text using Whisper
        Returns: (transcription, detected_language)
        """
        self._load_models()

        if self.whisper_model is None:
            return "Samahani, siwezi kusikia kwa sasa.", "sw"

        # Save to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name
        
        try:
            # Transcribe with Whisper
            result = self.whisper_model.transcribe(
                tmp_path,
                language=language or "sw",  # Default to Swahili
                task="transcribe",
                fp16=False
            )
            
            text = result["text"].strip()
            detected_lang = result.get("language", "sw")
            
            return text, detected_lang
            
        finally:
            os.unlink(tmp_path)
    
    async def text_to_speech(
        self, 
        text: str, 
        language: str = "sw",
        speaker_wav: Optional[str] = None
    ) -> bytes:
        """
        Convert text to speech with Swahili accent
        """
        self._load_models()

        if not HAS_TTS or self.tts_model is None:
            raise Exception("TTS is not available. Please install Coqui TTS and use Python 3.10/3.11.")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            output_path = tmp.name
        
        try:
            # Use TTS with speaker cloning if available, otherwise default
            if speaker_wav and os.path.exists(speaker_wav):
                self.tts_model.tts_to_file(
                    text=text,
                    speaker_wav=speaker_wav,
                    language=language,
                    file_path=output_path
                )
            else:
                # Generate with default speaker
                self.tts_model.tts_to_file(
                    text=text,
                    language=language,
                    file_path=output_path
                )
            
            with open(output_path, "rb") as f:
                audio_bytes = f.read()
            
            return audio_bytes
            
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    def add_swahili_expressions(self, text: str) -> str:
        """Add natural Swahili vocal expressions"""
        # Add breathing sounds, hesitations that sound natural
        expressions = {
            "um": "mmh",
            "uh": "ah",
            "hmm": "mmh",
            "oh": "ah",
            "well": "bas",
            "so": "bas",
            "you know": "unajua",
            "like": "kama"
        }
        
        # This would be used to guide TTS prosody
        return text
