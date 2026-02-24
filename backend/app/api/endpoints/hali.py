from fastapi import APIRouter
from ...models.schemas import HaliState, Mood, PersonalityUpdate
from ...core.personality.bro_engine import BroEngine
from ...utils.time_greetings import get_time_of_day

router = APIRouter()
bro_engine = BroEngine()

@router.get("/hali/current", response_model=HaliState)
async def get_current_hali():
    """Get Kioni's current mood/state"""
    time_of_day = get_time_of_day()
    
    return HaliState(
        current_mood=Mood(bro_engine.personality_state["mode"]),
        urafiki=bro_engine.personality_state["urafiki"],
        ucheshi=bro_engine.personality_state["ucheshi"],
        hekima=bro_engine.personality_state["hekima"],
        msaada=bro_engine.personality_state["msaada"],
        current_greeting=bro_engine.get_greeting(),
        time_of_day=time_of_day,
        active_sessions=1  # Would track actual sessions
    )

@router.post("/hali/update")
async def update_hali(update: PersonalityUpdate):
    """Update Kioni's personality settings"""
    update_dict = update.dict(exclude_unset=True)
    bro_engine.update_personality(update_dict)
    
    return {
        "status": "updated",
        "new_state": bro_engine.personality_state,
        "message": f"Kioni sasa yuko {update.mode.value if update.mode else 'same mode'}"
    }

@router.get("/hali/moods")
async def get_available_moods():
    """Get list of available moods"""
    return {
        "moods": [
            {"id": "poa", "name": "Poa", "description": "Chill and relaxed"},
            {"id": "safi", "name": "Safi", "description": "Good vibes only"},
            {"id": "mzito", "name": "Mzito", "description": "Serious and thoughtful"},
            {"id": "mchekeshaji", "name": "Mchekeshaji", "description": "Funny and energetic"},
            {"id": "mshauri", "name": "Mshauri", "description": "Supportive advisor"},
            {"id": "shughuli", "name": "Shughuli", "description": "Busy but available"}
        ]
    }