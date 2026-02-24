from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Optional
from ...models.schemas import ChatRequest, ChatResponse, ChatMessage, Language, Mood
from ...core.personality.bro_engine import BroEngine
from ...core.personality.swahili_processor import SwahiliProcessor
from ...core.ai_models.text_generator import TextGenerator
from ...core.personality.memory_manager import MemoryManager

router = APIRouter()
bro_engine = BroEngine()
swahili_processor = SwahiliProcessor()
text_generator = TextGenerator()
memory = MemoryManager()

@router.post("/chat", response_model=ChatResponse)
async def process_chat(request: ChatRequest):
    """Process text chat message"""
    try:
        # Detect language
        detected_lang = swahili_processor.detect_language(request.message)
        
        # Detect user mood
        user_mood = bro_engine.detect_mood_from_message(request.message)
        if request.mood_override:
            user_mood = request.mood_override
        
        # Get conversation context from memory
        context = await memory.get_context(request.session_id) if request.session_id else []
        
        # Generate system prompt based on mood
        system_prompt = bro_engine._build_system_prompt(
            user_mood, 
            bro_engine._is_deep_conversation(context),
            detected_lang == Language.SHENG
        )
        
        # Generate AI response
        ai_response_text = await text_generator.generate(
            messages=context + [ChatMessage(role="user", content=request.message, language=detected_lang)],
            system_prompt=system_prompt,
            language=detected_lang
        )
        
        # Fallback to rule-based if generation fails or is empty
        if not ai_response_text or len(ai_response_text) < 5:
            ai_response_text = bro_engine.generate_response(
                request.message,
                context,
                detected_lang,
                user_mood
            )
        
        # Create response message
        kioni_message = ChatMessage(
            role="kioni",
            content=ai_response_text,
            language=detected_lang
        )
        
        # Store in memory
        await memory.store_message(request.session_id, ChatMessage(role="user", content=request.message))
        await memory.store_message(request.session_id, kioni_message)
        
        # Update personality based on interaction
        bro_engine.update_personality({"mood": user_mood.value})
        
        return ChatResponse(
            message=kioni_message,
            personality_state=bro_engine.personality_state,
            detected_language=detected_lang
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Kioni amepata shida: {str(e)}")

@router.get("/greeting")
async def get_greeting():
    """Get time-appropriate greeting"""
    greeting = bro_engine.get_greeting()
    return {
        "greeting": greeting,
        "time_of_day": bro_engine._get_time_of_day(),
        "mood": bro_engine.personality_state["mode"]
    }

@router.post("/feedback")
async def process_feedback(session_id: str, feedback: dict):
    """Process user feedback to adjust personality"""
    bro_engine.update_personality(feedback)
    return {"status": "sawa", "updated_state": bro_engine.personality_state}