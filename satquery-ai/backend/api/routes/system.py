import platform
import psutil
import sys
import shutil
from fastapi import APIRouter
from pydantic import BaseModel
from loguru import logger

router = APIRouter(prefix="/system", tags=["System"])

class SystemInfo(BaseModel):
    cpu_count: int
    ram_total_gb: float
    ram_free_gb: float
    device: str
    cuda_available: bool
    gpu_name: str | None
    disk_free_gb: float
    python_version: str
    torch_version: str | None
    app_version: str

class SystemStatus(BaseModel):
    all_ready: bool
    components: dict[str, bool]

@router.get("/info", response_model=SystemInfo)
async def get_system_info():
    cuda_avail = False
    gpu_name = None
    torch_version = None
    device = "cpu"
    try:
        import torch
        torch_version = torch.__version__
        if torch.cuda.is_available():
            cuda_avail = True
            device = "cuda"
            gpu_name = torch.cuda.get_device_name(0)
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            device = "mps"
    except ImportError:
        pass

    ram = psutil.virtual_memory()
    disk = shutil.disk_usage("/")
    
    return SystemInfo(
        cpu_count=psutil.cpu_count(logical=True),
        ram_total_gb=round(ram.total / (1024**3), 2),
        ram_free_gb=round(ram.available / (1024**3), 2),
        device=device,
        cuda_available=cuda_avail,
        gpu_name=gpu_name,
        disk_free_gb=round(disk.free / (1024**3), 2),
        python_version=sys.version.split(" ")[0],
        torch_version=torch_version or "Not installed",
        app_version="1.0.0"
    )

@router.get("/status", response_model=SystemStatus)
async def get_system_status():
    components = {
        "geospatial_libs": False,
        "ml_libs": False,
        "database": True,
        "upload_dir": True,
        "model_cache": True
    }
    try:
        import rasterio
        components["geospatial_libs"] = True
    except ImportError:
        pass
        
    try:
        import torch
        import cv2
        components["ml_libs"] = True
    except ImportError:
        pass

    all_ready = all(components.values())
    return SystemStatus(all_ready=all_ready, components=components)
