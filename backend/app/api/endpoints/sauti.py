from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from typing import Optional
import base64
import io
from ...models.schemas import VoiceRequest, ChatRequest
from ...core.ai_models.speech_processor import SpeechProcessor
from ...core.personality.swahili_processor import SwahiliProcessor
from ...api.endpoints.mazungumzo import process_chat

router = APIRouter()
speech_processor = SpeechProcessor()
swahili_processor = SwahiliProcessor()

@router.post("/voice/upload")
async def process_voice_upload(
    audio: UploadFile = File(...),
    session_id: Optional[str] = None
):
    """Process uploaded voice file"""
    try:
        # Validate file
        if audio.size > 10 * 1024 * 1024:  # 10MB limit
            raise HTTPException(status_code=400, detail="File kubwa sana (max 10MB)")
        
        # Read audio
        audio_bytes = await audio.read()
        
        # Speech to text
        transcription, detected_lang = await speech_processor.speech_to_text(
            audio_bytes,
            language="sw"  # Default to Swahili
        )
        
        # Process as chat message
        chat_response = await process_chat(ChatRequest(
            message=transcription,
            session_id=session_id
        ))
        
        # Text to speech for response
        audio_response_b64 = None
        try:
            response_audio = await speech_processor.text_to_speech(
                chat_response.message.content,
                language="sw"
            )
            audio_response_b64 = base64.b64encode(response_audio).decode()
        except Exception as tts_err:
            print(f"TTS Error (skipping audio): {tts_err}")
        
        return {
            "transcription": transcription,
            "detected_language": detected_lang,
            "kioni_response": chat_response.message.content,
            "audio_response": audio_response_b64,
            "personality_state": chat_response.personality_state
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Shida na sauti: {str(e)}")

@router.post("/voice/base64")
async def process_voice_base64(request: VoiceRequest):
    """Process base64 encoded voice"""
    try:
        if len(request.audio_base64) > 15 * 1024 * 1024:  # Rough estimate for base64 of 10MB
            raise HTTPException(status_code=400, detail="Audio data is too large")

        audio_bytes = base64.b64decode(request.audio_base64)
        
        # Speech to text
        transcription, detected_lang = await speech_processor.speech_to_text(audio_bytes)
        
        # Process through chat
        from ...models.schemas import ChatRequest
        chat_response = await process_chat(ChatRequest(
            message=transcription,
            session_id=request.session_id
        ))
        
        # Generate voice response
        audio_response_b64 = None
        try:
            response_audio = await speech_processor.text_to_speech(
                chat_response.message.content,
                language="sw"
            )
            audio_response_b64 = base64.b64encode(response_audio).decode()
        except Exception as tts_err:
            print(f"TTS Error (skipping audio): {tts_err}")
        
        return {
            "transcription": transcription,
            "kioni_response": chat_response.message.content,
            "audio_response": audio_response_b64,
            "detected_language": detected_lang
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Shida: {str(e)}")

@router.get("/voice/test")
async def test_voice():
    """Test endpoint with simple Swahili phrase"""
    test_text = "Habari! Mimi ni Kioni. Niaje?"
    try:
        audio = await speech_processor.text_to_speech(test_text, language="sw")
        return StreamingResponse(
            io.BytesIO(audio),
            media_type="audio/wav",
            headers={"Content-Disposition": "attachment; filename=kioni_test.wav"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS is not available: {str(e)}")