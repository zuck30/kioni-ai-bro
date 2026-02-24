import httpx
from typing import AsyncGenerator, Optional, List, Dict, Any
from ...models.schemas import ChatMessage, Language
from ...config import settings

class TextGenerator:
    def __init__(self):
        self.hf_token = settings.HUGGINGFACE_TOKEN
        self.openrouter_key = settings.OPENROUTER_API_KEY
        self.primary_model = settings.TEXT_MODEL_PRIMARY
        self.fallback_model = settings.TEXT_MODEL_FALLBACK
        
        # Debug API keys (obscured)
        if self.hf_token:
            print(f"HF Token loaded: {self.hf_token[:5]}...{self.hf_token[-3:]}")
        else:
            print("HF Token NOT found in settings")

        if self.openrouter_key:
            print(f"OpenRouter Key loaded: {self.openrouter_key[:5]}...{self.openrouter_key[-3:]}")
        else:
            print("OpenRouter Key NOT found in settings")

    async def generate(
        self,
        messages: List[ChatMessage],
        system_prompt: str,
        language: Language = Language.MIXED,
        stream: bool = False
    ) -> str:
        """Generate text using Hugging Face Inference API or OpenRouter"""
        
        # Build conversation history
        conversation = self._build_prompt(messages, system_prompt, language)
        
        # Try primary model (Hugging Face)
        try:
            response = await self._call_hf_api(self.primary_model, conversation)
            return self._post_process(response, language)
        except Exception as e:
            print(f"Primary model error: {e}")
            # Try OpenRouter if available
            if self.openrouter_key:
                try:
                    response = await self._call_openrouter_api(conversation)
                    return self._post_process(response, language)
                except Exception as ore:
                    print(f"OpenRouter error: {ore}")

            # Fallback to secondary model (Hugging Face)
            try:
                response = await self._call_hf_api(self.fallback_model, conversation)
                return self._post_process(response, language)
            except:
                # Final fallback: simple rule-based response
                return self._fallback_response(messages[-1].content if messages else "Hello")
    
    def _build_prompt(
        self, 
        messages: List[ChatMessage], 
        system_prompt: str,
        language: Language
    ) -> str:
        """Build formatted prompt for the model"""
        prompt = f"<s>[INST] <<SYS>>\n{system_prompt}\n<</SYS>>\n\n"
        
        # Add conversation history
        for msg in messages[-5:]:  # Last 5 messages for context
            if msg.role == "user":
                prompt += f"{msg.content} [/INST]"
            else:
                prompt += f" {msg.content} </s><s>[INST] "
        
        # Add language instruction
        if language == Language.SWAHILI:
            prompt += "\n(Jibu kwa Kiswahili) "
        elif language == Language.MIXED:
            prompt += "\n(Mix Swahili and English naturally) "
        
        return prompt
    
    async def _call_hf_api(self, model: str, prompt: str) -> str:
        """Call Hugging Face Inference API"""
        api_url = f"https://api-inference.huggingface.co/models/{model}"
        headers = {"Authorization": f"Bearer {self.hf_token}"} if self.hf_token else {}
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 150,
                "temperature": 0.7,
                "top_p": 0.9,
                "do_sample": True,
                "return_full_text": False
            }
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(api_url, json=payload, headers=headers)
            response.raise_for_status()
            result = response.json()
            
            if isinstance(result, list) and len(result) > 0:
                return result[0].get("generated_text", "")
            return result.get("generated_text", "")

    async def _call_openrouter_api(self, prompt: str) -> str:
        """Call OpenRouter API as a robust fallback"""
        api_url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.openrouter_key}",
            "HTTP-Referer": "https://github.com/kioni-ai-bro",
            "X-Title": "Kioni AI Bro"
        }

        payload = {
            "model": "mistralai/mistral-7b-instruct:free",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 150,
            "temperature": 0.7
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(api_url, json=payload, headers=headers)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
    
    def _post_process(self, text: str, language: Language) -> str:
        """Clean up and format the response"""
        # Remove common AI artifacts
        text = text.replace("[/INST]", "").replace("</s>", "").strip()
        
        # Ensure it doesn't sound too robotic
        if "As an AI" in text or "I am an AI" in text:
            text = text.replace("As an AI", "As your bro").replace("I am an AI", "I'm Kioni")
        
        # Add Swahili warmth if appropriate
        if language in [Language.SWAHILI, Language.MIXED]:
            if not any(word in text.lower() for word in ["poa", "safi", "sawa", "bro", "kaka"]):
                text = "Sawa, " + text[0].lower() + text[1:]
        
        return text.strip()
    
    def _fallback_response(self, last_message: str) -> str:
        """Simple fallback when APIs fail"""
        return "Poa bro! Niko hapa, though my brain is taking a quick nap. Sema tena?"
    
    async def generate_stream(
        self,
        messages: List[ChatMessage],
        system_prompt: str
    ) -> AsyncGenerator[str, None]:
        """Stream response token by token"""
        # Implementation for streaming if needed
        full_response = await self.generate(messages, system_prompt)
        words = full_response.split()
        for word in words:
            yield word + " "