import uuid
import os
from pathlib import Path
from typing import List, Dict, Any
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from pydantic import BaseModel
from loguru import logger
import xxhash

# Mock database imports to fulfill the system requirements
# from backend.core.database import get_db, InputFile
# from backend.core.config import settings

router = APIRouter(prefix="/upload", tags=["Upload"])

class FileValidation(BaseModel):
    is_valid: bool
    checks_passed: List[str]
    checks_failed: List[str]
    warnings: List[str]
    error: str | None = None

class FileMetadata(BaseModel):
    file_id: str
    filename: str
    stored_path: str
    file_hash: str
    file_size_mb: float
    modality: str
    has_crs: bool
    width: int
    height: int
    band_count: int
    crs: str | None
    preview_url: str | None
    validation: FileValidation

class UploadResponse(BaseModel):
    file_ids: List[str]
    files: List[FileMetadata]

UPLOAD_DIR = Path("data/uploads")

@router.post("", response_model=UploadResponse)
async def upload_files(files: List[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    
    uploaded_files = []
    file_ids = []
    
    for file in files:
        file_id = str(uuid.uuid4())
        content = await file.read()
        file_hash = xxhash.xxh64(content).hexdigest()
        
        file_dir = UPLOAD_DIR / file_id
        file_dir.mkdir(parents=True, exist_ok=True)
        stored_path = file_dir / file.filename
        
        with open(stored_path, "wb") as f:
            f.write(content)
            
        file_size_mb = len(content) / (1024 * 1024)
        
        # Mock validation & extraction
        validation = FileValidation(
            is_valid=True,
            checks_passed=["format", "size"],
            checks_failed=[],
            warnings=[],
            error=None
        )
        
        metadata = FileMetadata(
            file_id=file_id,
            filename=file.filename,
            stored_path=str(stored_path),
            file_hash=file_hash,
            file_size_mb=round(file_size_mb, 2),
            modality="optical",
            has_crs=True,
            width=256,
            height=256,
            band_count=3,
            crs="EPSG:4326",
            preview_url=None, # Mock base64
            validation=validation
        )
        
        uploaded_files.append(metadata)
        file_ids.append(file_id)
        
    return UploadResponse(file_ids=file_ids, files=uploaded_files)
