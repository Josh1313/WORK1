import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from app.config import settings
from app.api.routes import chat, files, health
from app.services.storage import StorageService
from app.utils.logging import setup_logging

# Setup logging
logger = setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    # Startup
    logger.info(" Backend API starting up...")
    logger.info(f" Data directory: {settings.data_dir}")
    logger.info(f" Environment: {'Development' if settings.api_reload else 'Production'}")
    
    # Initialize storage
    storage = StorageService()
    await storage.initialize()
    
    logger.info("Backend is working properly and ready to accept connections!")
    logger.info(f"API available at: http://{settings.api_host}:{settings.api_port}")
    logger.info(" Waiting for frontend connections...")
    
    yield
    
    # Shutdown
    logger.info("Backend API shutting down...")
    await storage.cleanup()

# Create FastAPI app
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api", tags=["health"])  # Added prefix
app.include_router(files.router, prefix="/api/files", tags=["files"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])


if __name__ == "__main__":
    
    #sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload
    )