from datetime import datetime
from typing import Optional

def get_time_of_day(time_override: Optional[datetime] = None) -> str:
    """Determine time of day in Swahili context"""
    now = time_override or datetime.now()
    hour = now.hour
    
    if 5 <= hour < 10:
        return "asubuhi"      # Morning
    elif 10 <= hour < 16:
        return "mchana"       # Afternoon
    elif 16 <= hour < 19:
        return "jioni"        # Evening
    else:
        return "usiku"        # Night

def get_time_greeting(time_override: Optional[datetime] = None) -> str:
    """Get appropriate Swahili greeting for time of day"""
    time_of_day = get_time_of_day(time_override)
    
    greetings = {
        "asubuhi": "Habari za asubuhi",
        "mchana": "Habari za mchana", 
        "jioni": "Habari za jioni",
        "usiku": "Habari za usiku"
    }
    
    return greetings.get(time_of_day, "Habari")

def get_contextual_greeting(time_override: Optional[datetime] = None) -> str:
    """Get greeting with context (meal times, etc.)"""
    now = time_override or datetime.now()
    hour = now.hour
    
    if 7 <= hour < 9:
        return "Habari za asubuhi! Umeamkaje? Umeshapata chai?"
    elif 12 <= hour < 14:
        return "Habari za mchana! Umekula?"
    elif 18 <= hour < 20:
        return "Jioni njema! Umerudi kazini?"
    elif hour >= 22 or hour < 5:
        return "Usiku mwema! Bado uko awake?"
    
    return get_time_greeting(time_override)