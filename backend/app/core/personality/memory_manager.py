from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from ...models.schemas import ChatMessage
from ...models.database import db_manager
import json

class MemoryManager:
    def __init__(self):
        self.short_term_memory: Dict[str, List[ChatMessage]] = {}
        self.user_facts: Dict[str, Dict[str, Any]] = {}
        
    async def store_message(self, session_id: Optional[str], message: ChatMessage):
        """Store message in both short-term and long-term memory"""
        if not session_id:
            return
            
        # Short-term (in-memory)
        if session_id not in self.short_term_memory:
            self.short_term_memory[session_id] = []
        self.short_term_memory[session_id].append(message)
        
        # Keep only last 50 messages in short-term
        if len(self.short_term_memory[session_id]) > 50:
            self.short_term_memory[session_id] = self.short_term_memory[session_id][-50:]
        
        # Long-term (ChromaDB)
        await db_manager.store_conversation(session_id, {
            "id": message.id,
            "content": message.content,
            "role": message.role,
            "timestamp": message.timestamp.isoformat(),
            "language": message.language,
            "type": message.type,
            "emotion_score": message.emotion_score
        })
        
        # Extract and store facts
        await self._extract_facts(session_id, message)
    
    async def get_context(self, session_id: Optional[str], limit: int = 10) -> List[ChatMessage]:
        """Get recent conversation context"""
        if not session_id:
            return []
            
        # Try short-term first
        if session_id in self.short_term_memory:
            return self.short_term_memory[session_id][-limit:]
        
        # Fallback to long-term
        history = await db_manager.get_conversation_history(session_id, limit)
        return [ChatMessage(**msg) for msg in history]
    
    async def get_relevant_memories(self, session_id: str, query: str, n_results: int = 3) -> List[str]:
        """Get semantically similar past conversations"""
        results = await db_manager.search_similar(query, session_id, n_results)
        
        memories = []
        if results and results['documents']:
            for doc_list in results['documents']:
                memories.extend(doc_list)
        
        return memories
    
    async def _extract_facts(self, session_id: str, message: ChatMessage):
        """Extract key facts about user from messages"""
        if message.role != "user":
            return
            
        content = message.content.lower()
        
        if session_id not in self.user_facts:
            self.user_facts[session_id] = {
                "name": None,
                "location": None,
                "interests": [],
                "mood_history": [],
                "preferred_language": "mixed",
                "last_active": datetime.now()
            }
        
        # Extract name
        if "jina langu ni" in content or "my name is" in content:
            parts = content.replace("jina langu ni", "").replace("my name is", "").strip().split()
            if parts:
                self.user_facts[session_id]["name"] = parts[0].capitalize()
        
        # Extract location
        if "ninaishi" in content or "i live in" in content or "niko" in content:
            # Simple extraction - could be improved with NER
            pass
        
        # Track mood
        self.user_facts[session_id]["mood_history"].append({
            "timestamp": message.timestamp,
            "emotion": message.emotion_score
        })
        
        # Update language preference
        if message.language != "mixed":
            self.user_facts[session_id]["preferred_language"] = message.language
        
        self.user_facts[session_id]["last_active"] = datetime.now()
    
    def get_user_profile(self, session_id: str) -> Dict[str, Any]:
        """Get user profile with extracted facts"""
        return self.user_facts.get(session_id, {})
    
    def get_greeting_context(self, session_id: str) -> str:
        """Get personalized greeting context"""
        profile = self.get_user_profile(session_id)
        
        context_parts = []
        
        if profile.get("name"):
            context_parts.append(f"User's name is {profile['name']}")
        
        # Check last interaction time
        last_active = profile.get("last_active")
        if last_active:
            time_diff = datetime.now() - last_active
            if time_diff > timedelta(hours=12):
                context_parts.append("User hasn't chatted in a while")
        
        # Check interests for conversation starters
        interests = profile.get("interests", [])
        if interests:
            context_parts.append(f"User likes: {', '.join(interests[-3:])}")
        
        return " | ".join(context_parts) if context_parts else ""
    
    async def clear_session(self, session_id: str):
        """Clear all memory for a session"""
        if session_id in self.short_term_memory:
            del self.short_term_memory[session_id]
        if session_id in self.user_facts:
            del self.user_facts[session_id]
        await db_manager.delete_session(session_id)