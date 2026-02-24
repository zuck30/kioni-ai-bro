from fastapi import APIRouter, Depends
from ...config import settings
import httpx
from datetime import datetime

router = APIRouter()

@router.get("/debug/ai-status")
async def check_ai_status():
    """Check status of AI models and API keys"""
    results = {
        "timestamp": datetime.now().isoformat(),
        "keys_configured": {
            "huggingface": bool(settings.HUGGINGFACE_TOKEN),
            "openrouter": bool(settings.OPENROUTER_API_KEY)
        },
        "models": {
            "primary": settings.TEXT_MODEL_PRIMARY,
            "vision": settings.VISION_MODEL
        },
        "connectivity": {}
    }

    # Check HF connectivity
    if settings.HUGGINGFACE_TOKEN:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                hf_url = f"https://api-inference.huggingface.co/models/{settings.TEXT_MODEL_PRIMARY}"
                headers = {"Authorization": f"Bearer {settings.HUGGINGFACE_TOKEN}"}
                # Just a dummy request to check token
                response = await client.get(hf_url, headers=headers)
                results["connectivity"]["huggingface"] = "ok" if response.status_code != 401 else "invalid_token"
        except Exception as e:
            results["connectivity"]["huggingface"] = f"error: {str(e)}"
    else:
        results["connectivity"]["huggingface"] = "not_configured"

    # Check OpenRouter connectivity
    if settings.OPENROUTER_API_KEY:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                or_url = "https://openrouter.ai/api/v1/models"
                headers = {"Authorization": f"Bearer {settings.OPENROUTER_API_KEY}"}
                response = await client.get(or_url, headers=headers)
                results["connectivity"]["openrouter"] = "ok" if response.status_code == 200 else "invalid_key"
        except Exception as e:
            results["connectivity"]["openrouter"] = f"error: {str(e)}"
    else:
        results["connectivity"]["openrouter"] = "not_configured"

    return results
