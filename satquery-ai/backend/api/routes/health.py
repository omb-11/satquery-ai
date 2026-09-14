"""Health check route."""
from fastapi import APIRouter
from datetime import datetime
import psutil, platform
from backend.core.config import settings

router = APIRouter()

@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": settings.app_version,
        "timestamp": datetime.utcnow().isoformat(),
    }
