import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_chat_endpoint():
    """Test basic chat endpoint"""
    response = client.post("/api/chat", json={
        "message": "Habari Kioni!",
        "session_id": "test_session_123"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["message"]["role"] == "kioni"
    assert "detected_language" in data

def test_chat_swahili():
    """Test Swahili language detection"""
    response = client.post("/api/chat", json={
        "message": "Mambo vipi rafiki yangu",
        "session_id": "test_session_456"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["detected_language"] in ["sw", "mixed"]

def test_chat_sheng():
    """Test Sheng slang detection"""
    response = client.post("/api/chat", json={
        "message": "Niaje buda! Form ni gani?",
        "session_id": "test_session_789"
    })
    
    assert response.status_code == 200
    data = response.json()
    # Should detect as mixed or sheng
    assert data["detected_language"] in ["sheng", "mixed", "sw"]

def test_chat_personality_state():
    """Test that personality state is returned"""
    response = client.post("/api/chat", json={
        "message": "Test message",
        "session_id": "test_session"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "personality_state" in data
    assert "urafiki" in data["personality_state"]
    assert "ucheshi" in data["personality_state"]

def test_greeting_endpoint():
    """Test greeting endpoint"""
    response = client.get("/api/greeting")
    
    assert response.status_code == 200
    data = response.json()
    assert "greeting" in data
    assert "time_of_day" in data
    assert data["time_of_day"] in ["asubuhi", "mchana", "jioni", "usiku"]

def test_chat_with_context():
    """Test chat with conversation context"""
    context = [
        {"role": "user", "content": "Ninaitwa John", "type": "text", "language": "mixed"},
        {"role": "kioni", "content": "Karibu John!", "type": "text", "language": "mixed"}
    ]
    
    response = client.post("/api/chat", json={
        "message": "Unanikumbuka?",
        "session_id": "test_context",
        "context": context
    })
    
    assert response.status_code == 200

def test_invalid_request():
    """Test handling of invalid requests"""
    response = client.post("/api/chat", json={})
    assert response.status_code == 422  # Validation error