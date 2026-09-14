"""
SatQuery AI — Settings & Gemini AI Configuration Routes
Secure management of Gemini Analyst credentials and analysis precision modes.
Security Guarantee: Raw API keys are never returned back to the frontend.
"""
from __future__ import annotations
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from loguru import logger

from backend.core.config import settings
from backend.inference.gemini import GeminiAnalyst

router = APIRouter()

class GeminiConfigUpdate(BaseModel):
    api_key: Optional[str] = None
    model: Optional[str] = None

class PrecisionConfigUpdate(BaseModel):
    precision_mode: str  # fast | balanced | precise | expert

@router.get("/settings/gemini")
async def get_gemini_settings():
    """Return Gemini Analyst configuration status (masked for security)."""
    analyst = GeminiAnalyst()
    configured = analyst.is_configured()
    
    masked_key = ""
    if configured and analyst.api_key:
        masked_key = analyst.api_key[:4] + "*" * (len(analyst.api_key) - 8) + analyst.api_key[-4:]

    return {
        "configured": configured,
        "model": analyst.model,
        "masked_key": masked_key,
        "status": "READY" if configured else "NOT_CONFIGURED",
        "capabilities": ["Multimodal Interpretation", "Function Calling", "Structured Synthesis", "Zero-Hallucination"]
    }

@router.post("/settings/gemini")
async def update_gemini_settings(req: GeminiConfigUpdate):
    """Update runtime Gemini configuration."""
    if req.api_key is not None:
        settings.gemini_api_key = req.api_key.strip()
    if req.model is not None:
        settings.gemini_model = req.model.strip()

    analyst = GeminiAnalyst()
    logger.info(f"Updated Gemini configuration: model={analyst.model}, configured={analyst.is_configured()}")

    return {
        "status": "updated",
        "configured": analyst.is_configured(),
        "model": analyst.model
    }

@router.post("/settings/gemini/test")
async def test_gemini_connection():
    """Test connectivity and measure latency to Gemini API."""
    analyst = GeminiAnalyst()
    result = await analyst.test_connection()
    return result

@router.get("/settings/precision")
async def get_precision_settings():
    """Return current precision mode and effective threshold parameters."""
    return {
        "precision_mode": settings.precision_mode,
        "supported_modes": ["fast", "balanced", "precise", "expert"],
        "parameters": {
            "change_threshold": settings.change_threshold,
            "min_region_area_px": settings.min_region_area_px,
            "max_image_dim": settings.max_image_dim
        }
    }

@router.post("/settings/precision")
async def set_precision_settings(req: PrecisionConfigUpdate):
    """Set analysis precision mode."""
    if req.precision_mode not in ["fast", "balanced", "precise", "expert"]:
        raise HTTPException(status_code=400, detail="Invalid precision mode")
    
    settings.precision_mode = req.precision_mode
    return {"status": "updated", "precision_mode": settings.precision_mode}
