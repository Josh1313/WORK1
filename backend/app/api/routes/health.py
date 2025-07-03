from fastapi import APIRouter
from datetime import datetime
from app.config import settings

router = APIRouter()

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": settings.api_version,
        "message": "Backend is working properly!"
    }

@router.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Data Analysis API is running!",
        "docs": "/docs",
        "health": "/health"
    }