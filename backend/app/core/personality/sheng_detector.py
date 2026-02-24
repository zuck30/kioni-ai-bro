import re
from typing import List, Tuple

class ShengDetector:
    def __init__(self):
        self.sheng_dictionary = self._load_sheng()
        
    def _load_sheng(self) -> dict:
        """Load Sheng slang dictionary"""
        return {
            "greetings": ["niaje", "sasa", "vipi", "vipi mzee", "niaje mdogo wetu", "sasa joh"],
            "slang": ["poa", "freshi", "safi", "fiti", "buda", "mzee", "msee", "demu", "manzi", 
                     "balaa", "nganya", "Yohh", "chapa", "dunga", "ticha", "Chief", "Mkuu", 
                     "mazematic", "radar", "form", "mboka", "gava", "keja", "dedi", "chapaa"],
            "verbs": ["kuzaba", "kuchapa", "kudinya", "burebure", "kutravel", "kushow", "kuchangamsha"],
            "adjectives": ["mzee", "sio poa", "Mkali", "Boss", "chini", "juu", "noma", "tamu"]
        }
    
    def is_sheng(self, text: str) -> bool:
        """Detect if text contains Sheng"""
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        
        all_sheng = (
            self.sheng_dictionary["greetings"] + 
            self.sheng_dictionary["slang"] + 
            self.sheng_dictionary["verbs"] + 
            self.sheng_dictionary["adjectives"]
        )
        
        sheng_count = sum(1 for word in words if word in all_sheng)
        return sheng_count >= 1 or any(g in text_lower for g in self.sheng_dictionary["greetings"])
    
    def translate_to_swahili(self, text: str) -> str:
        """Translate common Sheng to Swahili"""
        translations = {
            r'\bniaje\b': "mambo vipi",
            r'\bsasa\b': "mambo",
            r'\bbuda\b': "kaka",
            r'\bmzee\b': "rafiki",
            r'\bmsee\b': "mtu",
            r'\bdame\b': "msichana",
            r'\bmanzi\b': "msichana",
            r'\bpisi\b': "msichana",
            r'\bmaokoto\b': "pesa",
            r'\bmali\b': "pesa",
            r'\bsonko\b': "tajiri",
            r'\bskuli\b': "shule",
            r'\bfees\b': "shule",
            r'\bmat\b': "matatu",
            r'\bnganya\b': "matatu",
            r'\bkeja\b': "nyumba",
            r'\bgava\b': "serikali",
            r'\bjoh\b': "chakula",
            r'\bmboka\b': "kazi"
        }
        
        result = text
        for pattern, replacement in translations.items():
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
        
        return result
    
    def get_sheng_response(self, intensity: str = "medium") -> str:
        """Generate Sheng-style response"""
        responses = {
            "light": ["Poa sana!", "Sawa sawa", "Freshi kabisa"],
            "medium": ["Niaje buda! Form ni gani?", "Sasa! Iko sawa?", "Poa! Tuko rada"],
            "heavy": ["Yoh! Niaje msee! Mboka iko aje?", "Sasa joh! Tuko rada kama buda", "Vipi mzee! Form ni kubamba tu"]
        }
        import random
        return random.choice(responses.get(intensity, responses["medium"]))