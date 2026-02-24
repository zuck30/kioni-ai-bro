from fastapi import APIRouter, HTTPException
from typing import Optional
from ...models.schemas import VisionRequest, VisionResponse
from ...core.ai_models.vision_analyzer import VisionAnalyzer
from ...core.personality.bro_engine import BroEngine

router = APIRouter()
vision_analyzer = VisionAnalyzer()
bro_engine = BroEngine()

@router.post("/vision/analyze", response_model=VisionResponse)
async def analyze_image(request: VisionRequest):
    """Analyze image from camera"""
    try:
        result = await vision_analyzer.analyze_image(
            request.image_base64,
            request.context
        )
        
        # Generate Kioni's reaction
        reaction = bro_engine.generate_vision_reaction(result)
        
        return VisionResponse(
            description=result["description"],
            objects=result["objects"],
            swahili_context=result["swahili_context"],
            mood_suggestion=result["mood_suggestion"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Shida na picha: {str(e)}")

@router.post("/vision/camera-frame")
async def process_camera_frame(frame_base64: str, session_id: Optional[str] = None):
    """Process periodic camera frame for context"""
    try:
        result = await vision_analyzer.analyze_image(frame_base64)
        
        # Only store significant changes
        if result["objects"] or "person" in result["description"].lower():
            # Could trigger proactive message from Kioni
            return {
                "context": result["swahili_context"],
                "notable_objects": result["objects"],
                "suggested_comment": bro_engine.generate_vision_comment(result)
            }
        
        return {"status": "no_significant_change"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))