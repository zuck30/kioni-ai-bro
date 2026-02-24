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
        
        if self.hf_token:
            print(f"HF Token loaded: {self.hf_token[:5]}...{self.hf_token[-3:]}")

    async def generate(
        self,
        messages: List[ChatMessage],
        system_prompt: str,
        language: Language = Language.MIXED,
        stream: bool = False
    ) -> str:
        conversation = self._build_prompt(messages, system_prompt, language)
        
        # Jaribu kutumia Hugging Face kwanza
        try:
            response = await self._call_hf_api(self.primary_model, conversation)
            return self._post_process(response, language)
        except Exception as e:
            print(f"Primary model error: {e}")
            
            # Kama HF imefeli (403/410), tumia OpenRouter mara moja
            if self.openrouter_key:
                try:
                    return await self._call_openrouter_api(conversation)
                except Exception as ore:
                    print(f"OpenRouter error: {ore}")

            return "Dah bro, mitambo imezidiwa. Nistue baada ya sekunde chache!"
    
    def _build_prompt(self, messages: List[ChatMessage], system_prompt: str, language: Language) -> str:
        prompt = f"<s>[INST] <<SYS>>\n{system_prompt}\n<</SYS>>\n\n"
        for msg in messages[-5:]:
            prompt += f"{msg.content} [/INST] " if msg.role == "user" else f"{msg.content} </s><s>[INST] "
        
        if language == Language.SWAHILI:
            prompt += "\n(Jibu kwa Kiswahili pekee) "
        return prompt
    
    async def _call_hf_api(self, model: str, prompt: str) -> str:
        # Hii URL ndiyo suluhisho la kudumu kwa sasa
        api_url = f"https://router.huggingface.co/hf-inference/models/{model}"
        
        headers = {
            "Authorization": f"Bearer {self.hf_token}",
            "Content-Type": "application/json",
            "x-wait-for-model": "true" 
        }
        
        payload = {
            "inputs": prompt,
            "parameters": {"max_new_tokens": 150, "temperature": 0.7, "do_sample": True}
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(api_url, json=payload, headers=headers)
            
            # Kama router bado inaleta shida ya 403, tujaribu direct inference kama backup ya haraka
            if response.status_code in [403, 401]:
                direct_url = f"https://api-inference.huggingface.co/models/{model}"
                response = await client.post(direct_url, json=payload, headers=headers)
            
            response.raise_for_status()
            result = response.json()
            return result[0].get("generated_text", "") if isinstance(result, list) else result.get("generated_text", "")

    async def _call_openrouter_api(self, prompt: str) -> str:
        api_url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.openrouter_key}",
            "HTTP-Referer": "http://localhost:8000",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "mistralai/mistral-7b-instruct",
            "messages": [{"role": "user", "content": prompt}]
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(api_url, json=payload, headers=headers)
            response.raise_for_status()
            res = response.json()
            return res["choices"][0]["message"]["content"]
    
    def _post_process(self, text: str, language: Language) -> str:
        return text.replace("[/INST]", "").replace("</s>", "").strip()

    async def generate_stream(self, messages: List[ChatMessage], system_prompt: str) -> AsyncGenerator[str, None]:
        full_response = await self.generate(messages, system_prompt)
        for word in full_response.split():
            yield word + " "