"""
SatQuery AI — FastAPI Main Application
"""
from __future__ import annotations
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from loguru import logger

from backend.core.config import settings
from backend.core.database import init_db
from backend.core.logging import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup/shutdown lifecycle."""
    setup_logging()
    settings.ensure_dirs()
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Device: {settings.get_device()}")
    await init_db()
    logger.info("Database initialized")
    yield
    logger.info("Shutting down SatQuery AI")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Agentic Earth Observation Intelligence — SIH 2026",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import all routers
from backend.api.routes.health import router as health_router
from backend.api.routes.system import router as system_router
from backend.api.routes.upload import router as upload_router
from backend.api.routes.validate import router as validate_router
from backend.api.routes.analyze import router as analyze_router
from backend.api.routes.models import router as models_router
from backend.api.routes.runs import router as runs_router
from backend.api.routes.reports import router as reports_router
from backend.api.routes.benchmark import router as benchmark_router
from backend.api.routes.training import router as training_router
from backend.api.routes.settings import router as settings_router

prefix = settings.api_prefix

app.include_router(health_router, prefix=prefix)
app.include_router(system_router, prefix=prefix)
app.include_router(upload_router, prefix=prefix)
app.include_router(validate_router, prefix=prefix)
app.include_router(analyze_router, prefix=prefix)
app.include_router(models_router, prefix=prefix)
app.include_router(runs_router, prefix=prefix)
app.include_router(reports_router, prefix=prefix)
app.include_router(benchmark_router, prefix=prefix)
app.include_router(training_router, prefix=prefix)
app.include_router(settings_router, prefix=prefix)

# Serve uploaded data as static files (with fallback)
import os
_data_dir = str(settings.data_dir)
os.makedirs(_data_dir, exist_ok=True)
app.mount("/data", StaticFiles(directory=_data_dir), name="data")


@app.get("/")
async def root():
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "description": "Agentic Earth Observation Intelligence Workstation",
        "api_docs": "/docs",
        "health": f"{prefix}/health",
    }
