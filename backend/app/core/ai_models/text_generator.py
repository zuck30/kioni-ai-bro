import httpx
import asyncio
from typing import AsyncGenerator, Optional, List
from ...models.schemas import ChatMessage, Language
from ...config import settings

class TextGenerator:
    def __init__(self):
        self.hf_token = settings.HUGGINGFACE_TOKEN
        self.openrouter_key = settings.OPENROUTER_API_KEY
        self.primary_model = settings.TEXT_MODEL_PRIMARY
        self.fallback_model = settings.TEXT_MODEL_FALLBACK
        print(f"DEBUG: KIONI Text Generator Ready.")
        print(f"   Primary: {self.primary_model}")
        print(f"   Fallback: {self.fallback_model}")

    async def generate(self, messages: List[ChatMessage], system_prompt: str, language: Language = Language.MIXED) -> str:
        conversation = self._build_prompt(messages, system_prompt, language)
        
        # Try OpenRouter first with correct model names
        if self.openrouter_key:
            print("DEBUG: Trying OpenRouter API...")
            result = await self._call_openrouter_api(conversation)
            if result:
                return result
        
        # Try Hugging Face with inference endpoint
        if self.hf_token:
            print("DEBUG: Trying Hugging Face API...")
            result = await self._call_huggingface_api(conversation)
            if result:
                return result
        
        # Fallback response
        return self._get_fallback_response()

    async def _call_openrouter_api(self, prompt: str) -> Optional[str]:
        """Call OpenRouter API with current model names"""
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.openrouter_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": "KIONI AI Bro"
        }
        
        # Current working models on OpenRouter (without :free suffix)
        models_to_try = [
            "mistralai/mistral-7b-instruct",  # This works
            "microsoft/phi-3-mini-4k-instruct",  # This works
            "google/gemma-2-9b-it"  # This works
        ]
        
        for model in models_to_try:
            try:
                payload = {
                    "model": model,
                    "messages": [
                        {
                            "role": "system", 
                            "content": f"You are KIONI, a friendly Swahili-speaking AI assistant. Respond in 1-2 short sentences. Be casual and helpful like a friend."
                        },
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 150,
                    "top_p": 0.9
                }
                
                print(f"DEBUG: Trying OpenRouter model: {model}")
                
                async with httpx.AsyncClient(timeout=45.0) as client:
                    response = await client.post(url, json=payload, headers=headers)
                    
                    if response.status_code == 200:
                        res = response.json()
                        if "choices" in res and len(res["choices"]) > 0:
                            text = res["choices"][0]["message"]["content"]
                            if text and len(text) > 5:
                                print(f"✅ OpenRouter success with {model}")
                                return self._post_process(text)
                    else:
                        try:
                            error = response.json()
                            print(f"DEBUG: OpenRouter {model} error: {error.get('error', {}).get('message', response.status_code)}")
                        except:
                            print(f"DEBUG: OpenRouter {model} returned {response.status_code}")
                        
            except Exception as e:
                print(f"DEBUG: OpenRouter error with {model}: {str(e)}")
                continue
        
        return None

    async def _call_huggingface_api(self, prompt: str) -> Optional[str]:
        """Call Hugging Face Inference API with correct endpoint"""
        
        # Models that work with the free inference API
        working_models = [
            "gpt2",  # Simple but works
            "facebook/bart-large-cnn",  # Good for text generation
            "google/flan-t5-base",  # Smaller but works
            "microsoft/phi-2"  # If available
        ]
        
        for model in working_models:
            try:
                # Use the inference endpoint
                url = f"https://api-inference.huggingface.co/models/{model}"
                headers = {
                    "Authorization": f"Bearer {self.hf_token}",
                    "Content-Type": "application/json",
                }
                
                # Different models need different parameters
                if "gpt2" in model:
                    payload = {
                        "inputs": prompt,
                        "parameters": {
                            "max_new_tokens": 100,
                            "temperature": 0.7,
                            "do_sample": True,
                            "return_full_text": False
                        }
                    }
                elif "flan" in model:
                    payload = {
                        "inputs": prompt,
                        "parameters": {
                            "max_new_tokens": 100,
                            "temperature": 0.7
                        }
                    }
                else:
                    payload = {
                        "inputs": prompt,
                        "parameters": {
                            "max_new_tokens": 100,
                            "temperature": 0.7
                        }
                    }
                
                print(f"DEBUG: Trying Hugging Face model: {model}")
                
                async with httpx.AsyncClient(timeout=60.0) as client:
                    response = await client.post(url, json=payload, headers=headers)
                    
                    if response.status_code == 200:
                        result = response.json()
                        text = self._extract_text(result)
                        if text and len(text) > 10:
                            print(f"✅ Hugging Face success with {model}")
                            return self._post_process(text)
                    elif response.status_code == 503:
                        print(f"DEBUG: {model} is loading, waiting...")
                        await asyncio.sleep(5)
                        # Retry once
                        response = await client.post(url, json=payload, headers=headers)
                        if response.status_code == 200:
                            result = response.json()
                            text = self._extract_text(result)
                            if text:
                                return self._post_process(text)
                    else:
                        print(f"DEBUG: Hugging Face {model} returned {response.status_code}")
                        
            except Exception as e:
                print(f"DEBUG: Hugging Face error with {model}: {str(e)}")
                continue
        
        return None

    def _extract_text(self, result):
        """Extract text from various response formats"""
        try:
            if isinstance(result, list) and len(result) > 0:
                if isinstance(result[0], dict):
                    return result[0].get("generated_text", "")
                return str(result[0])
            elif isinstance(result, dict):
                return result.get("generated_text", "")
            return str(result)
        except:
            return ""

    def _get_fallback_response(self) -> str:
        """Return a friendly fallback response"""
        fallbacks = [
            "Habari mwanangu! KIONI yuko hapa. Samahani mitambo ina shida kidogo, jaribu tena baada ya sekunde chache!",
            "Mambo vipi! Sorry, network imekataa kidogo. Tena jaribu kuongea nami!",
            "Niaje rafiki! Kuna hitch kidogo kwa connection. Rudia tena ombi lako!",
            "Sema! KIONI anakusikiliza lakini mitambo imechoka kidogo. Jaribu tena!"
        ]
        import random
        return random.choice(fallbacks)

    def _build_prompt(self, messages: List[ChatMessage], system_prompt: str, language: Language) -> str:
        """Build a clean, simple prompt"""
        # Get last 2 messages for context (keep it simple)
        recent_msgs = messages[-2:] if messages else []
        
        # Build a simple conversation
        conversation = system_prompt + "\n\n"
        
        for msg in recent_msgs:
            if msg.role == "user":
                conversation += f"User: {msg.content}\n"
            else:
                conversation += f"Assistant: {msg.content}\n"
        
        conversation += "Assistant: "
        
        # Keep prompt short to avoid token limits
        if len(conversation) > 500:
            conversation = conversation[-500:]
        
        return conversation

    def _post_process(self, text: str) -> str:
        """Clean up and shorten response"""
        # Remove any artifacts
        text = text.replace("Assistant:", "").replace("User:", "").strip()
        text = text.replace("[/INST]", "").replace("</s>", "").strip()
        
        # Make it sound like a friend
        if "As an AI" in text:
            text = text.replace("As an AI", "Mimi kama rafiki yako")
        
        # Keep it very short for better UX
        if len(text) > 200:
            text = text[:200] + "..."
        
        # If empty, return fallback
        if not text or len(text) < 3:
            text = "Sema mwanangu! Niko hapa kukusaidia."
        
        return text

    async def generate_stream(self, messages: List[ChatMessage], system_prompt: str) -> AsyncGenerator[str, None]:
        full_response = await self.generate(messages, system_prompt, Language.MIXED)
        for word in full_response.split():
            yield word + " "