import random
from typing import Dict, List, Optional, Any
from datetime import datetime
from ...models.schemas import Mood, ChatMessage, Language
from .swahili_processor import SwahiliProcessor
from .sheng_detector import ShengDetector
from .methali_db import MethaliDB
from ...utils.time_greetings import get_time_greeting, get_time_of_day
from ...config import settings

class BroEngine:
    def __init__(self):
        self.swahili_processor = SwahiliProcessor()
        self.sheng_detector = ShengDetector()
        self.methali_db = MethaliDB()
        self.personality_state = settings.DEFAULT_PERSONALITY.copy()
        self.conversation_history: List[ChatMessage] = []
        
    def get_greeting(self, time_override: Optional[datetime] = None) -> str:
        """Generate appropriate Swahili greeting based on time"""
        time_greeting = get_time_greeting(time_override)
        
        greetings = {
            "asubuhi": [
                "Habari za asubuhi! Umeamkaje mambo?",
                "Mambo vipi kaka! Asubuhi njema?",
                "Haya! Umeshapata chai ama bado?",
                "Good morning bro! Leo tunado?"
            ],
            "mchana": [
                "Mambo! Umekula ama bado?",
                "Habari za mchana! Siku ikuendaje?",
                "Niaje! Uko poa?",
                "Sasa! Tumalize hii siku vipi?"
            ],
            "jioni": [
                "Habari za jioni! Umechoka leo?",
                "Jioni njema! Siku imekuwa aje?",
                "Poa! Tuko home stretch sasa",
                "Vipi mzee! Tuko almost weekend?"
            ],
            "usiku": [
                "Habari za usiku! Bado uko awake?",
                "Usiku mwema! Mambo vipi?",
                "Haya! Time ya kustreet ama kulala?",
                "Still up? Story yako ni gani?"
            ]
        }
        
        time_key = get_time_of_day(time_override)
        return random.choice(greetings.get(time_key, greetings["mchana"]))
    
    def detect_mood_from_message(self, message: str) -> Mood:
        """Detect user mood to adjust Kioni's response style"""
        message_lower = message.lower()
        
        # Stress/Problem indicators
        stress_words = ["shida", "problem", "stress", "sad", "homa", "chungu", "ngumu", "lost", "fired"]
        if any(word in message_lower for word in stress_words):
            return Mood.MSHAURI
        

        success_words = ["promotion", "nimepata", "congrats", "sherehe", "wedding", "graduated", "passed"]
        if any(word in message_lower for word in success_words):
            return Mood.MCHEKESHAJI
        

        deep_words = ["maana", "meaning", "life", "future", "career", "relationship", "love", "family"]
        if any(word in message_lower for word in deep_words):
            return Mood.MZITO
        
        # Casual check
        casual_words = ["poa", "safi", "fiti", "freshi", "mzima"]
        if any(word in message_lower for word in casual_words):
            return Mood.POA
            
        return Mood.SAFI
    
    def generate_response(self, 
                         user_message: str, 
                         context: List[ChatMessage],
                         detected_language: Language,
                         user_mood: Mood) -> str:
        """Generate Kioni's response with authentic bro personality"""
        
        # Analyze conversation depth
        is_deep = self._is_deep_conversation(context)
        is_sheng = detected_language == Language.SHENG or self.sheng_detector.is_sheng(user_message)
        
        # Build personality prompt
        system_prompt = self._build_system_prompt(user_mood, is_deep, is_sheng)
        
        # Add cultural context
        if "shida" in user_message.lower() or "problem" in user_message.lower():
            methali = self.methali_db.get_relevant_proverb("struggle")
            response = self._comforting_response(user_message, methali, is_sheng)
        elif "success" in user_message.lower() or "nimepata" in user_message.lower():
            response = self._celebration_response(user_message, is_sheng)
        elif is_deep:
            response = self._deep_talk_response(user_message, is_sheng)
        else:
            response = self._casual_response(user_message, detected_language, is_sheng)
            
        return response
    
    def _build_system_prompt(self, mood: Mood, is_deep: bool, is_sheng: bool) -> str:
        """Build the personality context for responses"""
        base_traits = {
            Mood.POA: "Chill, relaxed, using 'poa', 'safi', casual",
            Mood.SAFI: "Balanced, friendly, helpful",
            Mood.MZITO: "Serious, thoughtful, wise, using proverbs",
            Mood.MCHEKESHAJI: "Funny, celebratory, energetic, using 'wueh!', 'mad!'",
            Mood.MSHAURI: "Supportive, gentle, patient, listening",
            Mood.SHUGHULI: "Brief, to the point, respectful of time"
        }
        
        trait = base_traits.get(mood, base_traits[Mood.SAFI])
        
        prompt = f"""You are KIONI, an AI friend from East Africa. 
Personality: {trait}
Language: Mix Swahili and English naturally (code-switching). Use Sheng if appropriate: {is_sheng}
Style: Talk like a real friend from the estate - genuine, sometimes sarcastic, always real.
Never sound like a robot or assistant. You're a bro, not a service.
Use local references: football, Bongo Flava, food, matatu culture when relevant.
"""
        if is_deep:
            prompt += "Be thoughtful. Share wisdom when appropriate but keep it real."
            
        return prompt
    
    def _comforting_response(self, message: str, methali: Optional[str], is_sheng: bool) -> str:
        """Generate supportive response for difficult times"""
        responses = [
            f"Pole sana kaka. {methali if methali else 'Kila kikuja na kwake'}. Niko nawe hapa.",
            "Haya, breathe kidogo. Tucheze hii story pole pole. What's really going on?",
            "Naskia uko down. Hii ni season tu, itapita. But for now, nikupee hug ama advice?",
            f"Wueh, that's heavy. {methali if methali else 'Mungu halali'}. Tukae chini tuchambue?"
        ]
        
        if is_sheng:
            responses = [r.replace("kaka", "buda").replace("haya", "sasa") for r in responses]
            
        return random.choice(responses)
    
    def _celebration_response(self, message: str, is_sheng: bool) -> str:
        """Generate celebration response"""
        responses = [
            "Wueh! Nilisema! Nilijua utafika! Sasa tunasherehekea wapi?",
            "Heey! Talent yako haikufichi! Leo tunakula nyama choma!",
            "Yeeeees! I knew it! Hii ni big deal, tukunywe soda ama?",
            "Mad! Congrats bro! Hii ni blessing. Next level sasa!"
        ]
        
        if is_sheng:
            responses.append("Form ni gani sasa? Tukubambe!")
            
        return random.choice(responses)
    
    def _deep_talk_response(self, message: str, is_sheng: bool) -> str:
        """Generate thoughtful response"""
        methali = self.methali_db.get_random_proverb()
        
        responses = [
            f"Unajua, wazee walisema '{methali}'. Maybe hii ni lesson yako sasa.",
            "Deep. Nakupata. Life ni journey, sio sprint. Tafakari kidogo.",
            "Hii ni heavy. But 'ukiona vyaelea, vimeundwa'. Kuna reason behind everything.",
            "Naskia uko confused. That's okay. Sometimes 'kupotea ni kujua njia'."
        ]
        
        return random.choice(responses)
    
    def _casual_response(self, message: str, lang: Language, is_sheng: bool) -> str:
        """Generate casual conversation"""
        if is_sheng:
            return random.choice([
                "Poa sana buda! Niaje?",
                "Sawa sawa! Form ni gani?",
                "Freshi! Uko area ama umetravel?",
                "Iko sawa! Tuko rada."
            ])
        
        if lang == Language.SWAHILI:
            return random.choice([
                "Poa! Habari yako?",
                "Safi! Umekula?",
                "Nzuri! Leo tunaenda aje?",
                "Mambo! Nikuhudumie aje?"
            ])
        
        return random.choice([
            "Safi bro! What's good?",
            "Poa! Been thinking about you actually.",
            "All good! You tell me, what's the vibe today?",
            "Cool cool! Got any tea to spill?"
        ])
    
    def _is_deep_conversation(self, context: List[ChatMessage]) -> bool:
        """Determine if conversation is getting deep"""
        if len(context) < 3:
            return False
        
        # Check recent messages for depth indicators
        recent = context[-3:]
        deep_indicators = ["feel", "think", "maana", "life", "future", "sad", "happy", "why", "kwa nini"]
        
        deep_count = sum(
            1 for msg in recent 
            for indicator in deep_indicators 
            if indicator in msg.content.lower()
        )
        
        return deep_count >= 2
    
    def _get_time_of_day(self) -> str:
        """Helper to get current time of day"""
        return get_time_of_day()

    def update_personality(self, feedback: Dict[str, Any]):
        """Adjust personality based on user feedback"""
        if "mood" in feedback:
            self.personality_state["mode"] = feedback["mood"]
        for trait in ["urafiki", "ucheshi", "hekima", "msaada"]:
            if trait in feedback:
                self.personality_state[trait] = max(0, min(100, feedback[trait]))