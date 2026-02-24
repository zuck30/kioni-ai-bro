from typing import Dict, List, Optional, Any
from enum import Enum
import random

class GestureType(Enum):
    GREETING = "greeting"
    LISTENING = "listening"
    THINKING = "thinking"
    SPEAKING = "speaking"
    EMPHATIC = "emphatic"
    COMFORTING = "comforting"
    CELEBRATING = "celebrating"
    CONFUSED = "confused"
    AGREEMENT = "agreement"

class GestureMapper:
    def __init__(self):
        self.gesture_library = self._load_gestures()
        
    def _load_gestures(self) -> Dict[GestureType, List[Dict[str, Any]]]:
        """Load African-inspired gesture definitions"""
        return {
            GestureType.GREETING: [
                {
                    "name": "kunyoosha_mkono",
                    "description": "Reaching out hand - East African greeting",
                    "keyframes": [
                        {"rotation": 0, "scale": 1, "translateY": 0},
                        {"rotation": -10, "scale": 1.1, "translateY": -20},
                        {"rotation": 0, "scale": 1, "translateY": 0}
                    ],
                    "duration": 1.5,
                    "easing": "easeInOut"
                },
                {
                    "name": "kichwa_nod",
                    "description": "Respectful head nod",
                    "keyframes": [
                        {"rotateX": 0},
                        {"rotateX": 15},
                        {"rotateX": 0},
                        {"rotateX": 10},
                        {"rotateX": 0}
                    ],
                    "duration": 1.0
                }
            ],
            
            GestureType.LISTENING: [
                {
                    "name": "sikiliza_sana",
                    "description": "Lean in to listen attentively",
                    "keyframes": [
                        {"scale": 1, "translateX": 0},
                        {"scale": 1.05, "translateX": 10},
                        {"scale": 1.02, "translateX": 5}
                    ],
                    "duration": 2.0,
                    "hold": True
                },
                {
                    "name": "tango_tango",
                    "description": "Gentle sway while listening",
                    "keyframes": [
                        {"rotate": -2},
                        {"rotate": 2},
                        {"rotate": -2}
                    ],
                    "duration": 3.0,
                    "repeat": True
                }
            ],
            
            GestureType.THINKING: [
                {
                    "name": "fikiria",
                    "description": "Hand to chin thinking pose",
                    "keyframes": [
                        {"rotate": 0, "scale": 1},
                        {"rotate": 5, "scale": 0.98},
                        {"rotate": -3, "scale": 0.98}
                    ],
                    "duration": 2.0,
                    "repeat": True
                },
                {
                    "name": "angalia_juu",
                    "description": "Look up while thinking",
                    "keyframes": [
                        {"translateY": 0},
                        {"translateY": -10},
                        {"translateY": -5}
                    ],
                    "duration": 1.5
                }
            ],
            
            GestureType.SPEAKING: [
                {
                    "name": "zungumza_mkono",
                    "description": "Hand gestures while speaking",
                    "keyframes": [
                        {"rotate": 0, "scale": 1},
                        {"rotate": -5, "scale": 1.02},
                        {"rotate": 5, "scale": 1.02},
                        {"rotate": 0, "scale": 1}
                    ],
                    "duration": 1.0,
                    "repeat": True
                },
                {
                    "name": "kichwa_tembea",
                    "description": "Head movement while talking",
                    "keyframes": [
                        {"rotateY": -5},
                        {"rotateY": 5},
                        {"rotateY": 0}
                    ],
                    "duration": 0.8,
                    "repeat": True
                }
            ],
            
            GestureType.EMPHATIC: [
                {
                    "name": "shtua",
                    "description": "Surprise/emphasis gesture",
                    "keyframes": [
                        {"scale": 1, "rotate": 0},
                        {"scale": 1.2, "rotate": -5},
                        {"scale": 1.1, "rotate": 0},
                        {"scale": 1, "rotate": 0}
                    ],
                    "duration": 0.6
                },
                {
                    "name": "pigia_makofi",
                    "description": "Clapping emphasis",
                    "keyframes": [
                        {"scaleX": 1},
                        {"scaleX": 0.8},
                        {"scaleX": 1.1},
                        {"scaleX": 1}
                    ],
                    "duration": 0.4
                }
            ],
            
            GestureType.COMFORTING: [
                {
                    "name": "kumbatia",
                    "description": "Comforting embrace gesture",
                    "keyframes": [
                        {"scale": 1, "translateY": 0},
                        {"scale": 1.05, "translateY": 5},
                        {"scale": 1.02, "translateY": 2}
                    ],
                    "duration": 2.0,
                    "hold": True
                },
                {
                    "name": "shika_mkono",
                    "description": "Holding hand gesture",
                    "keyframes": [
                        {"translateX": 0},
                        {"translateX": 10},
                        {"translateX": 5}
                    ],
                    "duration": 1.5
                }
            ],
            
            GestureType.CELEBRATING: [
                {
                    "name": "cheza",
                    "description": "Dance celebration",
                    "keyframes": [
                        {"rotate": 0, "scale": 1, "translateY": 0},
                        {"rotate": -10, "scale": 1.1, "translateY": -20},
                        {"rotate": 10, "scale": 1.1, "translateY": -20},
                        {"rotate": 0, "scale": 1, "translateY": 0}
                    ],
                    "duration": 1.0,
                    "repeat": True
                },
                {
                    "name": "tupa_mikono",
                    "description": "Throw hands up",
                    "keyframes": [
                        {"rotate": 0, "translateY": 0},
                        {"rotate": -15, "translateY": -30},
                        {"rotate": 15, "translateY": -30},
                        {"rotate": 0, "translateY": 0}
                    ],
                    "duration": 0.8
                }
            ],
            
            GestureType.CONFUSED: [
                {
                    "name": "shika_kichwa",
                    "description": "Hold head in confusion",
                    "keyframes": [
                        {"rotate": 0},
                        {"rotate": -8},
                        {"rotate": 8},
                        {"rotate": 0}
                    ],
                    "duration": 1.2
                },
                {
                    "name": "nyosha_shingo",
                    "description": "Cran neck to see better",
                    "keyframes": [
                        {"translateX": 0},
                        {"translateX": 15},
                        {"translateX": 0}
                    ],
                    "duration": 1.0
                }
            ],
            
            GestureType.AGREEMENT: [
                {
                    "name": "kubali_kichwa",
                    "description": "Nodding agreement",
                    "keyframes": [
                        {"rotateX": 0},
                        {"rotateX": 20},
                        {"rotateX": 0},
                        {"rotateX": 15},
                        {"rotateX": 0}
                    ],
                    "duration": 0.8
                },
                {
                    "name": "sawa_sawa",
                    "description": "Okay hand gesture",
                    "keyframes": [
                        {"scale": 1},
                        {"scale": 1.2},
                        {"scale": 1}
                    ],
                    "duration": 0.5
                }
            ]
        }
    
    def map_message_to_gesture(self, message: str, mood: str = "poa") -> Optional[Dict[str, Any]]:
        """Map message content to appropriate gesture"""
        message_lower = message.lower()
        
        # Detect intent
        if any(word in message_lower for word in ["habari", "mambo", "hello", "hi", "niaje"]):
            return self._get_gesture(GestureType.GREETING)
        
        if any(word in message_lower for word in ["pole", "sorry", "sad", "lost", "shida"]):
            return self._get_gesture(GestureType.COMFORTING)
        
        if any(word in message_lower for word in ["congrats", "poa", "safi", "wueh", "good", "promotion"]):
            return self._get_gesture(GestureType.CELEBRATING)
        
        if any(word in message_lower for word in ["maybe", "perhaps", "thinking", "fikiria"]):
            return self._get_gesture(GestureType.THINKING)
        
        if any(word in message_lower for word in ["yes", "ndio", "sawa", "true", "exactly"]):
            return self._get_gesture(GestureType.AGREEMENT)
        
        if "?" in message:
            return self._get_gesture(GestureType.CONFUSED)
        
        # Default based on mood
        mood_gestures = {
            "mzito": GestureType.THINKING,
            "mchekeshaji": GestureType.CELEBRATING,
            "mshauri": GestureType.LISTENING
        }
        
        return self._get_gesture(mood_gestures.get(mood, GestureType.SPEAKING))
    
    def _get_gesture(self, gesture_type: GestureType) -> Dict[str, Any]:
        """Get random gesture of specific type"""
        gestures = self.gesture_library.get(gesture_type, [])
        if gestures:
            return random.choice(gestures)
        return self.gesture_library[GestureType.SPEAKING][0]
    
    def get_idle_animation(self) -> Dict[str, Any]:
        """Get subtle idle animation"""
        return {
            "name": "pumzika",
            "description": "Breathing idle animation",
            "keyframes": [
                {"scale": 1, "translateY": 0},
                {"scale": 1.02, "translateY": -5},
                {"scale": 1, "translateY": 0}
            ],
            "duration": 4.0,
            "repeat": True,
            "easing": "easeInOut"
        }
    
    def combine_gestures(self, base_gesture: Dict[str, Any], overlay: Dict[str, Any]) -> Dict[str, Any]:
        """Combine two gestures for complex expressions"""
        return {
            "name": f"{base_gesture['name']}_{overlay['name']}",
            "keyframes": self._interpolate_keyframes(
                base_gesture["keyframes"],
                overlay["keyframes"]
            ),
            "duration": max(base_gesture["duration"], overlay["duration"])
        }
    
    def _interpolate_keyframes(self, kf1: List[Dict], kf2: List[Dict]) -> List[Dict]:
        """Simple keyframe interpolation"""
        # Simplified - in production would properly interpolate values
        return kf1 + kf2
    
    def generate_animation_css(self, gesture: Dict[str, Any]) -> str:
        """Generate CSS animation string from gesture definition"""
        keyframes = gesture.get("keyframes", [])
        duration = gesture.get("duration", 1.0)
        
        css = f"@keyframes {gesture['name']} {{\n"
        
        for i, kf in enumerate(keyframes):
            percentage = (i / (len(keyframes) - 1)) * 100 if len(keyframes) > 1 else 0
            css += f"  {percentage}% {{\n"
            
            for prop, value in kf.items():
                css_prop = self._map_property(prop)
                css += f"    {css_prop}: {value};\n"
            
            css += "  }\n"
        
        css += "}\n"
        css += f".{gesture['name']} {{\n"
        css += f"  animation: {gesture['name']} {duration}s "
        css += "infinite " if gesture.get("repeat") else ""
        css += f"{gesture.get('easing', 'ease')};\n"
        css += "}"
        
        return css
    
    def _map_property(self, prop: str) -> str:
        """Map internal property names to CSS"""
        mapping = {
            "rotate": "transform: rotate",
            "rotateX": "transform: rotateX",
            "rotateY": "transform: rotateY",
            "scale": "transform: scale",
            "scaleX": "transform: scaleX",
            "translateX": "transform: translateX",
            "translateY": "transform: translateY"
        }
        return mapping.get(prop, prop)

# Global instance
gesture_mapper = GestureMapper()