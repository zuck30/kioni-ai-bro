import chromadb
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
from ..config import settings

class ChromaDBManager:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
        self.collection = self.client.get_or_create_collection(
            name=settings.COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )
        
    async def store_conversation(self, session_id: str, message: Dict[str, Any], embedding: Optional[List[float]] = None):
        """Store conversation message with optional embedding"""
        doc_id = f"{session_id}_{message.get('id', datetime.now().timestamp())}"
        
        self.collection.add(
            documents=[message.get('content', '')],
            metadatas=[{
                "session_id": session_id,
                "role": message.get('role'),
                "timestamp": message.get('timestamp', datetime.now().isoformat()),
                "language": message.get('language', 'mixed'),
                "type": message.get('type', 'text'),
                "emotion_score": message.get('emotion_score', 0)
            }],
            ids=[doc_id],
            embeddings=[embedding] if embedding else None
        )
        
    async def get_conversation_history(self, session_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Retrieve conversation history for a session"""
        results = self.collection.get(
            where={"session_id": session_id},
            limit=limit
        )
        
        messages = []
        for i, doc in enumerate(results['documents']):
            messages.append({
                "id": results['ids'][i],
                "content": doc,
                **results['metadatas'][i]
            })
        
        # Sort by timestamp
        messages.sort(key=lambda x: x.get('timestamp', ''))
        return messages
    
    async def search_similar(self, query: str, session_id: Optional[str] = None, n_results: int = 5):
        """Search for similar past conversations"""
        filter_dict = {"session_id": session_id} if session_id else None
        
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=filter_dict
        )
        
        return results
    
    async def delete_session(self, session_id: str):
        """Delete all messages for a session"""
        self.collection.delete(
            where={"session_id": session_id}
        )
    
    async def get_user_interests(self, session_id: str) -> List[str]:
        """Extract user interests from conversation history"""
        history = await self.get_conversation_history(session_id, limit=50)
        
        # Simple keyword extraction for interests
        interest_keywords = ["football", "music", "food", "work", "family", "politics", "tech"]
        interests = []
        
        for msg in history:
            content = msg.get('content', '').lower()
            for keyword in interest_keywords:
                if keyword in content and keyword not in interests:
                    interests.append(keyword)
        
        return interests

# Global instance
db_manager = ChromaDBManager()