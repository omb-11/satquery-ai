"""
SatQuery AI — Core Configuration
"""
from __future__ import annotations
import os
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field


BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    # App
    app_name: str = "SatQuery AI"
    app_version: str = "1.0.0"
    debug: bool = False

    # Paths
    base_dir: Path = BASE_DIR
    data_dir: Path = BASE_DIR / "data"
    model_cache_dir: Path = BASE_DIR / "models" / "cache"
    upload_dir: Path = BASE_DIR / "data" / "uploads"
    results_dir: Path = BASE_DIR / "data" / "results"
    reports_dir: Path = BASE_DIR / "data" / "reports"
    demo_data_dir: Path = BASE_DIR / "demo_data"

    # Database
    database_url: str = f"sqlite+aiosqlite:///{BASE_DIR}/data/satquery.db"

    # Device
    device: str = "auto"  # auto | cpu | cuda | mps
    enable_gpu: bool = True
    max_image_dim: int = 1024
    max_upload_mb: int = 500

    # Models
    default_vlm_model: str = "Salesforce/blip-image-captioning-base"
    enable_remote_models: bool = False
    ollama_base_url: str = "http://localhost:11434"

    # Analysis
    change_threshold: float = 0.15
    min_region_area_px: int = 50
    max_change_regions: int = 20
    confidence_min_threshold: float = 0.3

    # API
    api_prefix: str = "/api/v1"
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    def get_device(self) -> str:
        if self.device != "auto":
            return self.device
        try:
            import torch
            if torch.cuda.is_available():
                return "cuda"
            elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                return "mps"
        except ImportError:
            pass
        return "cpu"

    def ensure_dirs(self):
        for d in [self.data_dir, self.model_cache_dir, self.upload_dir,
                  self.results_dir, self.reports_dir]:
            d.mkdir(parents=True, exist_ok=True)


settings = Settings()
