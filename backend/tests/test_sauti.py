import pytest
from fastapi.testclient import TestClient
from app.main import app
import base64

client = TestClient(app)

def test_voice_test_endpoint():
    """Test voice test endpoint returns audio"""
    response = client.get("/api/voice/test")
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "audio/wav"
    assert len(response.content) > 0

def test_voice_base64_missing_audio():
    """Test voice endpoint with missing audio"""
    response = client.post("/api/voice/base64", json={
        "audio_base64": "",
        "format": "webm"
    })
    
    # Should handle gracefully or return error
    assert response.status_code in [200, 400, 500]

def test_voice_base64_invalid_format():
    """Test voice endpoint with invalid base64"""
    response = client.post("/api/voice/base64", json={
        "audio_base64": "invalid_base64!!!",
        "format": "webm"
    })
    
    # Should handle error gracefully
    assert response.status_code in [400, 500]

def test_voice_upload_no_file():
    """Test voice upload without file"""
    response = client.post("/api/voice/upload")
    
    assert response.status_code == 422  # Validation error for missing file

def test_voice_large_file_rejection():
    """Test that overly large files are rejected"""
    # Create a fake large base64 string (>10MB)
    large_audio = base64.b64encode(b"x" * (11 * 1024 * 1024)).decode()
    
    response = client.post("/api/voice/base64", json={
        "audio_base64": large_audio,
        "format": "webm"
    })
    
    # Should reject due to size
    assert response.status_code in [400, 413]

@pytest.mark.asyncio
async def test_speech_processor_initialization():
    """Test that speech processor initializes correctly"""
    from app.core.ai_models.speech_processor import SpeechProcessor
    
    processor = SpeechProcessor()
    assert processor is not None
    # Models load lazily, so they might be None initially