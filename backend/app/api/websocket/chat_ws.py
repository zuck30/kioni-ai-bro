from fastapi import WebSocket, WebSocketDisconnect
import json
import base64
from typing import Dict, Set
from ...core.personality.bro_engine import BroEngine
from ...core.ai_models.text_generator import TextGenerator
from ...core.ai_models.speech_processor import SpeechProcessor
from ...core.ai_models.vision_analyzer import VisionAnalyzer
from ...models.schemas import WebSocketMessage, ChatMessage, Language

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        
    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        
    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            
    async def send_personal_message(self, message: dict, client_id: str):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_json(message)
            
    async def broadcast(self, message: dict):
        for connection in self.active_connections.values():
            await connection.send_json(message)

manager = ConnectionManager()
bro_engine = BroEngine()
text_generator = TextGenerator()
speech_processor = SpeechProcessor()
vision_analyzer = VisionAnalyzer()

async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    
    try:
        # Send greeting
        greeting = bro_engine.get_greeting()
        await manager.send_personal_message({
            "type": "system",
            "payload": {
                "message": greeting,
                "hali": bro_engine.personality_state
            }
        }, client_id)
        
        while True:
            # Receive message
            data = await websocket.receive_text()
            message = json.loads(data)
            
            msg_type = message.get("type")
            
            if msg_type == "chat":
                await handle_chat_message(client_id, message["payload"])
            elif msg_type == "voice":
                await handle_voice_message(client_id, message["payload"])
            elif msg_type == "vision":
                await handle_vision_message(client_id, message["payload"])
            elif msg_type == "typing":
                await handle_typing_indicator(client_id, message["payload"])
                
    except WebSocketDisconnect:
        manager.disconnect(client_id)
        await manager.broadcast({
            "type": "system",
            "payload": {"message": f"Kioni ametulia (Client {client_id} left)"}
        })

async def handle_chat_message(client_id: str, payload: dict):
    """Handle text chat via WebSocket"""
    user_message = payload["message"]
    session_id = payload.get("session_id", client_id)
    
    # Send typing indicator
    await manager.send_personal_message({
        "type": "typing",
        "payload": {"status": "start"}
    }, client_id)
    
    # Process message
    from ...core.personality.swahili_processor import SwahiliProcessor
    swahili_processor = SwahiliProcessor()
    
    detected_lang = swahili_processor.detect_language(user_message)
    user_mood = bro_engine.detect_mood_from_message(user_message)
    
    # Generate response
    system_prompt = bro_engine._build_system_prompt(
        user_mood,
        False,
        detected_lang == Language.SHENG
    )
    
    response_text = await text_generator.generate(
        messages=[ChatMessage(role="user", content=user_message, language=detected_lang)],
        system_prompt=system_prompt,
        language=detected_lang
    )
    
    # Stop typing
    await manager.send_personal_message({
        "type": "typing",
        "payload": {"status": "stop"}
    }, client_id)
    
    # Generate audio response
    audio_response_b64 = None
    try:
        # We use Swahili as default for voice, or detect from text
        tts_lang = "sw" if detected_lang.value in ["sw", "sheng", "mixed"] else "en"
        audio_bytes = await speech_processor.text_to_speech(response_text, language=tts_lang)
        audio_response_b64 = base64.b64encode(audio_bytes).decode()
    except Exception as e:
        print(f"TTS Error: {e}")

    # Send response
    await manager.send_personal_message({
        "type": "chat",
        "payload": {
            "message": response_text,
            "role": "kioni",
            "language": detected_lang.value,
            "mood": user_mood.value,
            "audio": audio_response_b64
        }
    }, client_id)

async def handle_voice_message(client_id: str, payload: dict):
    """Handle voice message"""
    audio_base64 = payload["audio"]
    audio_bytes = base64.b64decode(audio_base64)
    
    # Transcribe
    transcription, lang = await speech_processor.speech_to_text(audio_bytes)
    
    # Process as chat but capture the response to avoid double processing
    # For now, we'll just call handle_chat_message which now includes TTS
    await handle_chat_message(client_id, {
        "message": transcription,
        "session_id": payload.get("session_id", client_id)
    })

async def handle_vision_message(client_id: str, payload: dict):
    """Handle camera frame"""
    image_base64 = payload["image"]
    
    result = await vision_analyzer.analyze_image(image_base64)
    
    # Generate contextual comment
    comment = bro_engine.generate_vision_comment(result)
    
    await manager.send_personal_message({
        "type": "vision",
        "payload": {
            "analysis": result,
            "kioni_comment": comment
        }
    }, client_id)

async def handle_typing_indicator(client_id: str, payload: dict):
    """Broadcast typing status"""
    await manager.broadcast({
        "type": "typing",
        "payload": payload
    })