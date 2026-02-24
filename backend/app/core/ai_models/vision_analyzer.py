import io
import base64
from typing import Dict, List, Any, Optional
from PIL import Image
import torch
from transformers import AutoModelForCausalLM, AutoProcessor
from ...config import settings

class VisionAnalyzer:
    def __init__(self):
        self.model = None
        self.processor = None
        self.hf_token = settings.HUGGINGFACE_TOKEN
        
    def _load_model(self):
        """Authenticated load for Moondream2 on Mac MPS"""
        if self.model is None:
            try:
                model_id = settings.VISION_MODEL or "vikhyatk/moondream2"
                device = "mps" if torch.backends.mps.is_available() else "cpu"
                print(f"Loading vision model {model_id} on {device}...")
                
                # ADDED TOKEN PARAMETER
                self.processor = AutoProcessor.from_pretrained(
                    model_id, 
                    trust_remote_code=True, 
                    token=self.hf_token
                )
                self.model = AutoModelForCausalLM.from_pretrained(
                    model_id,
                    trust_remote_code=True,
                    token=self.hf_token,
                    torch_dtype=torch.float32
                ).to(device)
                print("Vision model loaded successfully!")
            except Exception as e:
                print(f"CRITICAL ERROR loading vision model: {e}")

    async def analyze_image(self, image_base64: str, context: Optional[str] = None) -> Dict[str, Any]:
        self._load_model()
        if not self.model:
            return {"description": "Vision offline", "swahili_context": "Macho yangu yana giza."}

        try:
            if "," in image_base64:
                image_base64 = image_base64.split(",")[1]
            
            image = Image.open(io.BytesIO(base64.b64decode(image_base64)))
            prompt = "Describe this image:"
            
            inputs = self.processor(image, prompt, return_tensors="pt").to(self.model.device)
            with torch.no_grad():
                output = self.model.generate(**inputs, max_new_tokens=100)
            
            description = self.processor.decode(output[0], skip_special_tokens=True).strip()
            
            return {
                "description": description,
                "swahili_context": f"Nimeona: {description}",
                "mood_suggestion": "poa"
            }
        except Exception as e:
            print(f"Analysis error: {e}")
            return {"description": "Error analyzing image", "swahili_context": "Kizunguzungu!"}