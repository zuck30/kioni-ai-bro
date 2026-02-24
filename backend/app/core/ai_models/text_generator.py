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
        print(f"DEBUG: KIONI Text Generator Ready. Primary: {self.primary_model}")

    async def generate(self, messages: List[ChatMessage], system_prompt: str, language: Language = Language.MIXED) -> str:
        conversation = self._build_prompt(messages, system_prompt, language)
        
        # URL ZA KUJARIBU (Moja ikifeli, inahamia nyingine)
        endpoints = [
            # 1. Direct Inference (Njia ya uhakika zaidi kwa model za Mistral)
            f"https://api-inference.huggingface.co/models/{self.primary_model}",
            # 2. Router API (Kama backup)
            f"https://router.huggingface.co/hf-inference/models/{self.primary_model}",
            # 3. Fallback Model Direct
            f"https://api-inference.huggingface.co/models/{self.fallback_model}"
        ]

        for url in endpoints:
            try:
                print(f"DEBUG: Testing endpoint: {url}")
                headers = {
                    "Authorization": f"Bearer {self.hf_token}",
                    "Content-Type": "application/json",
                    "x-wait-for-model": "true"
                }
                payload = {
                    "inputs": conversation,
                    "parameters": {"max_new_tokens": 150, "temperature": 0.7}
                }
                
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(url, json=payload, headers=headers)
                    
                    if response.status_code == 200:
                        result = response.json()
                        text = result[0].get("generated_text", "") if isinstance(result, list) else result.get("generated_text", "")
                        if text:
                            return self._post_process(text)
                    else:
                        print(f"DEBUG: URL {url} returned {response.status_code}")
                        
            except Exception as e:
                print(f"DEBUG: Error with {url}: {e}")

        # NJIA YA MWISHO: OpenRouter (Hii ikifeli basi intaneti ina shida)
        if self.openrouter_key:
            try:
                print("DEBUG: Trying OpenRouter as last resort...")
                return await self._call_openrouter_api(conversation)
            except Exception as e:
                print(f"DEBUG: OpenRouter also failed: {e}")

        return "Dah mwanangu, mitambo ya mawasiliano imekataa kabisa. Hebu refresh page!"

    async def _call_openrouter_api(self, prompt: str) -> str:
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.openrouter_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "mistralai/mistral-7b-instruct",
            "messages": [{"role": "user", "content": prompt}]
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            res = response.json()
            return self._post_process(res["choices"][0]["message"]["content"])

    def _build_prompt(self, messages: List[ChatMessage], system_prompt: str, language: Language) -> str:
        # Prompt fupi ili kuzuia makosa ya token limits
        prompt = f"<s>[INST] <<SYS>>\n{system_prompt}\n<</SYS>>\n\n"
        for msg in messages[-3:]:
            if msg.role == "user":
                prompt += f"{msg.content} [/INST] "
            else:
                prompt += f"{msg.content} </s><s>[INST] "
        return prompt

    def _post_process(self, text: str) -> str:
        # Safisha mabaki ya tags
        text = text.replace("[/INST]", "").replace("</s>", "").replace("<s>", "").strip()
        # Badilisha 'As an AI' iwe lugha ya kishikaji
        if "As an AI" in text:
            text = text.replace("As an AI", "Mimi kama bro wako")
        return text

    async def generate_stream(self, messages: List[ChatMessage], system_prompt: str) -> AsyncGenerator[str, None]:
        full_response = await self.generate(messages, system_prompt)
        for word in full_response.split():
            yield word + " "