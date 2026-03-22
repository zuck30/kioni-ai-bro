import io
import base64
import tempfile
import os
import asyncio
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

try:
    import edge_tts
    HAS_EDGE_TTS = True
except ImportError:
    HAS_EDGE_TTS = False

if not HAS_TTS and not HAS_EDGE_TTS:
    print("Warning: Neither Coqui TTS nor edge-tts found. Voice responses will be disabled.")

from ...config import settings


class SpeechProcessor:
    def __init__(self):
        self.whisper_model = None
        self.tts_model = None
        
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

        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name
        
        try:
            result = self.whisper_model.transcribe(
                tmp_path,
                language=language or "sw",
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
        speaker_wav: Optional[str] = None,
        voice_style: str = "natural"
    ) -> bytes:

        self._load_models()

        if HAS_TTS and self.tts_model is not None:
            try:
                return await self._generate_coqui_tts(text, language, speaker_wav)
            except Exception as e:
                print(f"Coqui TTS failed: {e}, falling back to edge-tts")

        if HAS_EDGE_TTS:
            return await self._generate_edge_tts(text, language, voice_style)

        raise Exception("No TTS engine available. Please install Coqui TTS or edge-tts.")

    async def _generate_coqui_tts(self, text: str, language: str, speaker_wav: Optional[str]) -> bytes:
        """Generate speech using Coqui TTS"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            output_path = tmp.name
        
        try:
            if speaker_wav and os.path.exists(speaker_wav):
                self.tts_model.tts_to_file(
                    text=text,
                    speaker_wav=speaker_wav,
                    language=language,
                    file_path=output_path
                )
            else:
                self.tts_model.tts_to_file(
                    text=text,
                    language=language,
                    file_path=output_path
                )
            
            with open(output_path, "rb") as f:
                return f.read()
            
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)

    async def _generate_edge_tts(
        self, 
        text: str, 
        language: str = "sw",
        style: str = "natural"
    ) -> bytes:


        voices = {
            "sw": "sw-KE-RafikiNeural",  
            "sw-ke": "sw-KE-RafikiNeural",  
            "sw-tz": "sw-TZ-RehemaNeural",  
            "en": "en-US-GuyNeural", 
            "en-gb": "en-GB-RyanNeural"  
        }
        
        
        if language == "sw":
            voice = "sw-KE-RafikiNeural"
        else:
            voice = voices.get(language, "sw-KE-RafikiNeural")

        rate = "+0%"
        pitch = "+0Hz"
        
        if style == "cheerful":
            rate = "+10%"
            pitch = "+5Hz"
        elif style == "empathetic":
            rate = "-5%"
            pitch = "-2Hz"
        elif style == "authoritative":
            rate = "-5%"
            pitch = "-10Hz"

        try:
            communicate = edge_tts.Communicate(
                text=text, 
                voice=voice,
                rate=rate,
                pitch=pitch
            )
            
            audio_data = b""
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data += chunk["data"]

            if not audio_data:
                raise Exception("No audio data received from edge-tts")

            return audio_data
            
        except Exception as e:
            print(f"Edge TTS error with {voice}: {e}")
            raise

    def preprocess_swahili_text(self, text: str) -> str:
        """Preprocess Swahili text for better TTS pronunciation."""
        import re
        
        text = re.sub(r'([.!?])([A-Z])', r'\1 \2', text)
        
        replacements = {
            "kwa mf.": "kwa mfano",
            "v.v.": "viwango vya",
            "nb.": "kumbuka",
            "ing.": "ingawa",
            "mk.": "mke",
            "bw.": "bwana",
            "bi.": "bibi"
        }
        
        for abbr, full in replacements.items():
            text = text.replace(abbr, full)
        
        return text.strip()

    def add_natural_expressions(self, text: str, mood: str = "neutral") -> str:
        """Add natural Kenyan Swahili expressions."""
        import random
        
        if mood == "greeting":
            expressions = ["Eeh", "Sasa", "Vipi"]
            if random.random() < 0.2 and not text.startswith(tuple(expressions)):
                filler = random.choice(expressions)
                text = f"{filler}, {text}"
        
        elif mood == "thinking":
            if not text.startswith(("Eeh", "Sasa", "Vipi")):
                text = f"Eeh, {text}"
        
        return text

    async def speak(
        self, 
        text: str, 
        language: str = "sw",
        natural: bool = True,
        mood: str = "neutral",
        style: str = "natural"
    ) -> bytes:
        """
        High-level method to convert text to natural-sounding speech with MALE KENYAN voice.
        
        Args:
            text: Text to speak
            language: Language code (sw for Swahili)
            natural: Whether to apply natural preprocessing
            mood: Context mood (neutral, greeting, thinking)
            style: Voice style (natural, cheerful, empathetic, authoritative)
        """
        if natural:
            text = self.preprocess_swahili_text(text)
            text = self.add_natural_expressions(text, mood)
        
        return await self.text_to_speech(text, language, voice_style=style)

    def get_voice_info(self) -> dict:
        """Return information about the male Kenyan voice being used."""
        return {
            "primary_voice": "sw-KE-RafikiNeural",
            "description": "Male Kenyan Swahili voice - natural and authentic",
            "gender": "Male",
            "language": "Swahili (Kenya)",
            "characteristics": "Clear, natural, friendly tone with authentic Kenyan accent",
            "fallback_voice": "sw-TZ-RehemaNeural",
            "available_styles": ["natural", "cheerful", "empathetic", "authoritative"]
        }


async def test_tts():
    """Test the TTS with Male Kenyan voice"""
    processor = SpeechProcessor()
    
    print("Voice Info:", processor.get_voice_info())
    print("\n" + "="*50)
    
    test_texts = [
        ("Habari yako rafiki? Leo ni siku nzuri sana.", "greeting"),
        ("Eeh, unataka nikusaidie nini leo?", "greeting"),
        ("Sawa, nitakusaidia na hilo. Subiri kidogo.", "thinking"),
        ("Asante sana kwa kutumia huduma yetu. Kwaheri!", "neutral")
    ]
    
    for text, mood in test_texts:
        print(f"\nGenerating: {text}")
        print(f"Mood: {mood}")
        
        audio = await processor.speak(text, mood=mood, style="natural")
        
        filename = f"male_kenyan_swahili_{hash(text)}.mp3"
        with open(filename, "wb") as f:
            f.write(audio)
        print(f"Saved: {filename} ({len(audio)} bytes)")
    
    print("\n" + "="*50)
    print("All audio files generated with MALE KENYAN voice (Rafiki)")

# Run test
if __name__ == "__main__":
    asyncio.run(test_tts())