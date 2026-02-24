import re
from typing import Tuple, List
from langdetect import detect
from ...models.schemas import Language

class SwahiliProcessor:
    def __init__(self):
        self.swahili_words = self._load_swahili_vocab()
        self.english_common = set(["the", "and", "is", "are", "was", "were", "have", "has", "had", "do", "does", "did", "will", "would", "could", "should"])
        
    def _load_swahili_vocab(self) -> set:
        """Core Swahili vocabulary"""
        return set([
            "mambo", "habari", "poa", "safi", "asante", "karibu", "tafadhali",
            "samahani", "ndio", "hapana", "sawa", "nzuri", "mzuri", "wewe",
            "mimi", "sisi", "nyinyi", "yeye", "wao", "ni", "wa", "ya", "za",
            "kwa", "cha", "vya", "lako", "yako", "zake", "angu", "ako", "etu",
            "nyama", "choma", "ugali", "sukuma", "wiki", "chai", "kahawa",
            "asubuhi", "mchana", "jioni", "usiku", "leo", "kesho", "jana",
            "rafiki", "kaka", "dada", "ndugu", "mzee", "kijana", "mtu", "watu"
        ])
    
    def detect_language(self, text: str) -> Language:
        """Detect if text is Swahili, English, Sheng, or mixed"""
        words = re.findall(r'\b\w+\b', text.lower())
        
        swahili_count = sum(1 for w in words if w in self.swahili_words)
        english_count = sum(1 for w in words if w in self.english_common)
        
        total_words = len(words)
        if total_words == 0:
            return Language.ENGLISH
            
        swahili_ratio = swahili_count / total_words
        english_ratio = english_count / total_words
        
        # Check for code-switching
        if swahili_ratio > 0.3 and english_ratio > 0.3:
            return Language.MIXED
        elif swahili_ratio > 0.6:
            return Language.SWAHILI
        elif english_ratio > 0.6:
            return Language.ENGLISH
        
        # Try langdetect as fallback
        try:
            detected = detect(text)
            if detected == 'sw':
                return Language.SWAHILI
            elif detected == 'en':
                return Language.ENGLISH
        except:
            pass
            
        return Language.MIXED
    
    def extract_entities(self, text: str) -> List[dict]:
        """Extract culturally relevant entities"""
        entities = []
        
        # Food mentions
        foods = ["ugali", "nyama", "choma", "sukuma", "pilau", "biriani", "mandazi", "chai"]
        for food in foods:
            if food in text.lower():
                entities.append({"type": "food", "value": food})
        

        times = ["asubuhi", "mchana", "jioni", "usiku", "leo", "kesho"]
        for time in times:
            if time in text.lower():
                entities.append({"type": "time", "value": time})
        

        relations = ["rafiki", "kaka", "dada", "mama", "baba", "mzee"]
        for rel in relations:
            if rel in text.lower():
                entities.append({"type": "relation", "value": rel})
                
        return entities
    
    def normalize_sheng(self, text: str) -> str:
        """Convert common Sheng to standard Swahili for processing"""
        sheng_map = {
            "niaje": "mambo vipi",
            "poa": "poa",
            "sawa": "sawa",
            "freshi": "safi",
            "buda": "kaka",
            "mzee": "rafiki",
            "sasa": "mambo",
            "form": "hali",
            "radar": "tuko",
            "mboka": "kazi",
            "dedi": "kifo",
            "chapaa": "pesa",
            "msee": "mtu",
            "dame": "msichana",
            "manzi": "msichana",
            "mboch": "msichana",
            "tichi": "shule",
            "fees": "shule",
            "rieng": "njia",
            "joh": "chakula",
            "kanju": "kanisa",
            "mat": "matatu",
            "nganya": "matatu",
            "mali": "pesa",
            "sonko": "tajiri",
            "mblo": "mwanamke",
            "chapa": "piga",
            "dunga": "choma",
            "ticha": "mwalimu",
            "ngwati": "nguo",
            "dedi": "kifo",
            "mazematic": "hesabu",
            "mazem": "hesabu"
        }
        
        result = text
        for sheng, swahili in sheng_map.items():
            result = re.sub(r'\b' + sheng + r'\b', swahili, result, flags=re.IGNORECASE)
        
        return result