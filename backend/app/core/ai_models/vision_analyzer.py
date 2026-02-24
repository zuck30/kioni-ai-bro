import io
import base64
from typing import Dict, List, Any, Optional
from PIL import Image
import torch
from transformers import AutoModelForVision2Seq, AutoProcessor
from ...config import settings

class VisionAnalyzer:
    def __init__(self):
        self.model = None
        self.processor = None
        self._load_model()
        
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
        """Load Moondream or similar lightweight vision model"""
        if self.model is None:
            print("Loading vision model...")
            model_id = settings.VISION_MODEL
            
            self.processor = AutoProcessor.from_pretrained(model_id)
            self.model = AutoModelForVision2Seq.from_pretrained(
                model_id,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto"
            )
    
    async def analyze_image(
        self, 
        image_base64: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Analyze image and return culturally-aware description"""
        # Decode image
        image_bytes = base64.b64decode(image_base64)
        image = Image.open(io.BytesIO(image_bytes))
        
        # Generate caption
        prompt = "Describe this image in detail:"
        if context:
            prompt = f"Context: {context}\nDescribe what you see:"
        
        inputs = self.processor(image, prompt, return_tensors="pt")
        
        with torch.no_grad():
            output = self.model.generate(**inputs, max_new_tokens=100)
        
        description = self.processor.decode(output[0], skip_special_tokens=True)
        
        # Add Swahili cultural context
        swahili_desc = self._add_cultural_context(description)
        
        # Detect objects with cultural significance
        objects = self._detect_cultural_objects(description)
        
        # Suggest mood based on scene
        mood = self._suggest_mood(description, objects)
        
        return {
            "description": description,
            "swahili_context": swahili_desc,
            "objects": objects,
            "mood_suggestion": mood
        }
    
    def _add_cultural_context(self, description: str) -> str:
        """Add East African context to description"""
        desc_lower = description.lower()
        
        # Check for food
        if any(word in desc_lower for word in ["food", "meal", "plate", "eating"]):
            return f"Kuna chakula hapa! {description} Inaonekana tamu sana."
        
        # Check for transport
        if any(word in desc_lower for word in ["car", "vehicle", "bus", "van"]):
            return f"Transport! {description} Labda ni matatu ya route flani?"
        
        # Check for people
        if "person" in desc_lower or "people" in desc_lower:
            return f"Watu! {description} Wanakaa wako poa."
        
        # Default
        return f"Nawaona! {description}"
    
    def _detect_cultural_objects(self, description: str) -> List[Dict[str, Any]]:
        """Detect culturally significant objects"""
        detected = []
        desc_lower = description.lower()
        
        for obj, meaning in self.cultural_objects.items():
            if obj.replace("_", " ") in desc_lower or obj in desc_lower:
                detected.append({
                    "object": obj,
                    "meaning": meaning,
                    "cultural_significance": "high"
                })
        
        return detected
    
    def _suggest_mood(self, description: str, objects: List[Dict]) -> str:
        """Suggest Kioni's mood based on scene"""
        desc_lower = description.lower()
        
        if any(word in desc_lower for word in ["party", "celebration", "smile", "happy"]):
            return "mchekeshaji"
        elif any(word in desc_lower for word in ["work", "office", "computer", "study"]):
            return "mzito"
        elif any(word in desc_lower for word in ["food", "eat", "drink", "chai"]):
            return "rafiki"
        else:
            return "poa"