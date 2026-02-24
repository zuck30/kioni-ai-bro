from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from datetime import datetime

from .api.endpoints import mazungumzo, sauti, picha, hali, debug
from .api.websocket import chat_ws
from .config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("KIONI inaanza... (Kioni is starting)")
    yield
    # Shutdown
    print("KIONI analala... (Kioni is sleeping)")

app = FastAPI(
    title=settings.APP_NAME,
    description="KIONI - Your Swahili-speaking AI Bro",
    version=settings.VERSION,
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(mazungumzo.router, prefix="/api", tags=["mazungumzo"])
app.include_router(sauti.router, prefix="/api", tags=["sauti"])
app.include_router(picha.router, prefix="/api", tags=["picha"])
app.include_router(hali.router, prefix="/api", tags=["hali"])
app.include_router(debug.router, prefix="/api", tags=["debug"])

# WebSocket
@app.websocket("/ws/chat/{client_id}")
async def websocket_route(websocket: WebSocket, client_id: str):
    await chat_ws.websocket_endpoint(websocket, client_id)

@app.get("/")
async def root():
    return {
        "message": "KIONI API - Rafiki Yako wa AI",
        "status": "online",
        "version": settings.VERSION,
        "endpoints": {
            "chat": "/api/chat",
            "voice": "/api/voice/upload",
            "vision": "/api/vision/analyze",
            "hali": "/api/hali/current",
            "websocket": "/ws/chat/{client_id}"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "poa", "timestamp": datetime.now().isoformat()}