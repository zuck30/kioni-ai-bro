import io
import base64
from typing import Dict, List, Any, Optional
from PIL import Image
import torch
import os

# We import directly. If this fails, the server crash will tell us EXACTLY why.
from transformers import AutoModelForCausalLM, AutoProcessor

from ...config import settings

class VisionAnalyzer:
    def __init__(self):
        self.model = None
        self.processor = None
        
        # Swahili cultural objects database
        self.cultural_objects = {
            "matatu": "public transport van with colorful graffiti",
            "kanga": "colorful fabric wrap with Swahili proverbs",
            "kitenge": "African wax print fabric",
            "kikoi": "traditional woven cloth",
            "nyama_choma": "grilled meat, usually goat or beef",
            "ugali": "stiff cornmeal porridge",
            "sukuma_wiki": "collard greens",
            "chai": "tea with milk and spices",
            "jiko": "charcoal stove",
            "mkahawa": "local cafe",
            "vibandas": "small kiosks/shops"
        }
        
    def _load_model(self):
        """Lazy load Moondream or similar lightweight vision model"""
        if self.model is None:
            try:
                # Check PyTorch version for compatibility
                torch_version = torch.__version__
                if torch_version < "2.4.0":
                    print(f"WARNING: PyTorch {torch_version} detected. Vision models (Moondream2) usually require PyTorch >= 2.4.0 for proper functionality.")
                    print("To fix this, run: pip install --upgrade torch torchvision torchaudio")

                print(f"Loading vision model: {settings.VISION_MODEL}...")
                model_id = settings.VISION_MODEL

                # Optimized for Mac M-series (MPS)
                device = "cpu"
                dtype = torch.float32
                
                if torch.backends.mps.is_available():
                    device = "mps"
                    # Moondream sometimes struggles with float16 on MPS, float32 is safer
                    dtype = torch.float32 
                elif torch.cuda.is_available():
                    device = "cuda"
                    dtype = torch.float16

                print(f"Using device: {device}")

                self.processor = AutoProcessor.from_pretrained(model_id, trust_remote_code=True)
                self.model = AutoModelForCausalLM.from_pretrained(
                    model_id,
                    trust_remote_code=True,
                    torch_dtype=dtype,
                ).to(device)
                
                print("Vision model loaded successfully!")
            except Exception as e:
                print(f"CRITICAL ERROR loading vision model: {str(e)}")
                # This will now show you if you are missing 'einops' or 'timm'
                self.model = None
                self.processor = None
    
    async def analyze_image(
        self, 
        image_base64: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Analyze image and return culturally-aware description"""
        self._load_model()

        if self.model is None or self.processor is None:
            return {
                "description": "Nimeshindwa kuona picha hii kwa sasa (Model not available)",
                "swahili_context": "Pole, nimepata shida kidogo na macho yangu ya AI.",
                "objects": [],
                "mood_suggestion": "poa"
            }

        try:
            # Decode image
            image_bytes = base64.b64decode(image_base64)
            image = Image.open(io.BytesIO(image_bytes))
            
            # Generate caption
            prompt = "Describe this image in detail:"
            if context:
                prompt = f"Context: {context}\nDescribe what you see:"
            
            # Move inputs to same device as model
            device = next(self.model.parameters()).device
            inputs = self.processor(image, prompt, return_tensors="pt").to(device)
            
            with torch.no_grad():
                output = self.model.generate(**inputs, max_new_tokens=100)
            
            description = self.processor.decode(output[0], skip_special_tokens=True)
            
            return {
                "description": description,
                "swahili_context": self._add_cultural_context(description),
                "objects": self._detect_cultural_objects(description),
                "mood_suggestion": self._suggest_mood(description, [])
            }
        except Exception as e:
            print(f"Analysis error: {e}")
            return {"description": "Error analyzing image", "swahili_context": "Shida ya kiufundi.", "objects": [], "mood_suggestion": "huzuni"}
    
    def _add_cultural_context(self, description: str) -> str:
        desc_lower = description.lower()
        if any(word in desc_lower for word in ["food", "meal", "plate"]):
            return f"Kuna chakula hapa! {description} Inaonekana tamu sana."
        if any(word in desc_lower for word in ["car", "vehicle", "van"]):
            return f"Transport! {description} Labda ni matatu ya route flani?"
        return f"Nawaona! {description}"
    
    def _detect_cultural_objects(self, description: str) -> List[Dict[str, Any]]:
        detected = []
        desc_lower = description.lower()
        for obj, meaning in self.cultural_objects.items():
            if obj.replace("_", " ") in desc_lower:
                detected.append({"object": obj, "meaning": meaning, "cultural_significance": "high"})
        return detected
    
    def _suggest_mood(self, description: str, objects: List[Dict]) -> str:
        desc_lower = description.lower()
        if "happy" in desc_lower or "smile" in desc_lower: return "mchekeshaji"
        return "poa"