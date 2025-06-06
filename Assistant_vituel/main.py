import asyncio
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.routes import app as api_app
from app.utils.logger import setup_logger
from app.models.database import init_database

logger = setup_logger(_name_)

def create_app() -> FastAPI:
    """Factory pour créer l'application FastAPI"""
    
    app = FastAPI(
        title="AI Assistant Maître de Cérémonie",
        description="Assistant IA pour salons et événements",
        version="1.0.0",
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None
    )
    
    # Middleware CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_HOSTS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Inclure les routes de l'API
    app.mount("/", api_app)
    
    return app

# Créer l'instance de l'application
app = create_app()

@app.on_event("startup")
async def startup():
    """Initialisation au démarrage"""
    logger.info("🚀 Starting AI Assistant MC")
    
    # Initialiser la base de données
    await init_database()
    
    logger.info("✅ Application started successfully")

@app.on_event("shutdown")
async def shutdown():
    """Nettoyage à l'arrêt"""
    logger.info("🛑 Shutting down AI Assistant MC")

if _name_ == "_main_":
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )