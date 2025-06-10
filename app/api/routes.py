from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import json
import asyncio

from app.config import settings
from app.models.database import get_db, SessionLocal
from app.models.salon import ExhibitorResponse, ExhibitorCreate
from app.services.voice_service import VoiceService
from app.services.vision_service import VisionService
from app.agents.mc_agent import MasterOfCeremoniesAgent
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

app = FastAPI(
    title="AI Assistant Maître de Cérémonie",
    description="Assistant IA pour salons et événements",
    version="1.0.0"
)

# Services globaux
voice_service = VoiceService()
vision_service = VisionService()
mc_agent = None  # Initialisé au démarrage

# Templates et fichiers statiques
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Gestionnaire de connexions WebSocket
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                await self.disconnect(connection)

manager = ConnectionManager()

# Routes API
@app.get("/")
async def dashboard():
    """Dashboard principal"""
    return templates.TemplateResponse("dashboard.html", {"request": {}})

@app.get("/api/health")
async def health_check():
    """Vérification de l'état de l'application"""
    return {
        "status": "healthy",
        "services": {
            "voice": await voice_service.test_connection(),
            "vision": vision_service.is_camera_available(),
            "agent": mc_agent is not None
        }
    }

@app.get("/api/exhibitors", response_model=List[ExhibitorResponse])
async def get_exhibitors(db: Session = Depends(get_db)):
    """Récupère la liste des exposants"""
    # Implémentation avec SQLAlchemy
    pass

@app.post("/api/exhibitors", response_model=ExhibitorResponse)
async def create_exhibitor(
    exhibitor: ExhibitorCreate, 
    db: Session = Depends(get_db)
):
    """Crée un nouvel exposant"""
    # Implémentation avec SQLAlchemy
    pass

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket pour communication temps réel"""
    await manager.connect(websocket)
    try:
        while True:
            # Recevoir les messages du client
            data = await websocket.receive_json()
            
            if data["type"] == "voice_command":
                # Traiter la commande vocale
                response = await mc_agent.process_interaction(data["message"])
                await websocket.send_json({
                    "type": "agent_response",
                    "message": response
                })
                
            elif data["type"] == "start_listening":
                # Commencer l'écoute
                audio_text = await voice_service.listen_async()
                if audio_text:
                    await websocket.send_json({
                        "type": "speech_recognized",
                        "text": audio_text
                    })
                    
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.on_event("startup")
async def startup_event():
    """Initialisation au démarrage"""
    global mc_agent
    logger.info("Starting AI Assistant MC application")
    
    # Initialiser les services
    await voice_service.initialize()
    vision_service.start_camera()
    
    # Charger les données du salon
    salon_data = load_salon_data()
    mc_agent = MasterOfCeremoniesAgent(salon_data)
    
    logger.info("Application started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Nettoyage à l'arrêt"""
    logger.info("Shutting down application")
    vision_service.stop_camera()
