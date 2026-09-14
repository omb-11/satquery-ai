"""
SatQuery AI — Models Route
Returns real model registry from ModelRegistry.
"""
from typing import List, Optional, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from loguru import logger

router = APIRouter()


class ModelInfo(BaseModel):
    id: str
    name: str
    version: str
    status: str
    task_types: List[str]
    modalities: List[str]
    device: str
    checkpoint: Optional[str] = None
    fallback: Optional[str] = None
    description: str = ""


@router.get("/models", response_model=List[ModelInfo])
async def list_models():
    """List all registered specialists and their status."""
    try:
        from backend.inference.registry import ModelRegistry
        registry = ModelRegistry()
        status_table = registry.get_status_table()
        models = []
        for entry in status_table:
            models.append(ModelInfo(
                id=entry.get("id", entry.get("name", "unknown")),
                name=entry.get("name", "unknown"),
                version=entry.get("version", "1.0"),
                status=entry.get("status", "unknown"),
                task_types=entry.get("task_types", []),
                modalities=entry.get("modalities", []),
                device=entry.get("device", "cpu"),
                checkpoint=entry.get("checkpoint"),
                fallback=entry.get("fallback"),
                description=entry.get("description", ""),
            ))
        return models
    except Exception as e:
        logger.error(f"Models list error: {e}")
        # Return static fallback registry
        return _static_registry()


@router.get("/models/{model_id}")
async def get_model(model_id: str):
    """Get detail for a specific model."""
    try:
        from backend.inference.registry import ModelRegistry
        registry = ModelRegistry()
        spec = registry.get_specialist(model_id)
        if spec:
            return spec
        raise HTTPException(status_code=404, detail=f"Model '{model_id}' not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _static_registry() -> List[ModelInfo]:
    """Static fallback model list."""
    return [
        ModelInfo(id="remote_sensing_vqa", name="BLIP VQA (CPU)", version="1.0",
                  status="fallback", task_types=["vqa", "captioning"],
                  modalities=["optical", "rgb"], device="cpu",
                  checkpoint="Salesforce/blip-image-captioning-base",
                  fallback="MockProvider",
                  description="VQA and captioning via BLIP. Uses MockProvider if model not downloaded."),
        ModelInfo(id="change_detection", name="Classical Change Detector", version="1.0",
                  status="ready", task_types=["change_detection", "change_vqa"],
                  modalities=["optical", "multispectral"], device="cpu",
                  description="Threshold-based change detection with morphological filtering."),
        ModelInfo(id="sar_processor", name="SAR Backscatter Analyzer", version="1.0",
                  status="ready", task_types=["sar_analysis"],
                  modalities=["sar"], device="cpu",
                  description="Classical SAR normalization, water and built-up detection."),
        ModelInfo(id="optical_sar_fusion", name="Optical-SAR Fusion Engine", version="1.0",
                  status="ready", task_types=["optical_sar_fusion"],
                  modalities=["optical", "sar"], device="cpu",
                  description="Spectral + SAR evidence fusion with agreement scoring."),
        ModelInfo(id="grounding", name="Spectral Grounding Analyzer", version="1.0",
                  status="ready", task_types=["grounding", "object_identification"],
                  modalities=["optical", "multispectral"], device="cpu",
                  description="Text-guided grounding using spectral indices and thresholding."),
        ModelInfo(id="spectral_analyzer", name="Spectral Index Analyzer", version="1.0",
                  status="ready", task_types=["land_cover", "ndvi", "ndwi"],
                  modalities=["optical", "multispectral"], device="cpu",
                  description="NDVI, NDWI, NDBI computation from multispectral bands."),
        ModelInfo(id="geospatial_preprocessor", name="Rasterio Preprocessor", version="1.0",
                  status="ready", task_types=["preprocessing", "metadata"],
                  modalities=["optical", "sar", "multispectral"], device="cpu",
                  description="GeoTIFF reading, CRS detection, reprojection, tiling."),
        ModelInfo(id="bigearthnet_adapter", name="BigEarthNet RS Adapter", version="0.0",
                  status="not_installed",
                  task_types=["rs_adaptation"], modalities=["optical", "sar"], device="cpu",
                  checkpoint=None, fallback="Base VLM",
                  description="Lightweight RS domain adaptation via projection head. Run training/train_rs_adapter.py to enable."),
        ModelInfo(id="report_generator", name="Report Generator", version="1.0",
                  status="ready", task_types=["report"],
                  modalities=[], device="cpu",
                  description="HTML and JSON report generation from analysis state."),
    ]
