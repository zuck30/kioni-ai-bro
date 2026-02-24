from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from datetime import datetime
import importlib

from .api.endpoints import mazungumzo, sauti, picha, hali, debug
from .api.websocket import chat_ws
from .config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    print(f"--- {settings.APP_NAME} Startup ---")
    print(f"Version: {settings.VERSION}")
    
    # Check for TTS availability without masking the error
    try:
        importlib.import_module("edge_tts")
        print("Voice Engine (edge-tts): READY")
    except ImportError:
        print("Voice Engine (edge-tts): NOT INSTALLED. Voice will be disabled.")

    print("KIONI inaanza... (Kioni is starting)")
    yield
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
    allow_origins=["*"],
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

@app.websocket("/ws/chat/{client_id}")
async def websocket_route(websocket: WebSocket, client_id: str):
    await chat_ws.websocket_endpoint(websocket, client_id)

@app.get("/")
async def root():
    return {
        "message": "KIONI API - Rafiki Yako wa AI",
        "status": "online",
        "version": settings.VERSION
    }

@app.get("/health")
async def health_check():
    return {"status": "poa", "timestamp": datetime.now().isoformat()}