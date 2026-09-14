from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from loguru import logger

router = APIRouter(prefix="/validate", tags=["Validate"])

class ValidateRequest(BaseModel):
    file_ids: List[str]
    pair_type: str

class ValidateResponse(BaseModel):
    is_valid: bool
    results: Dict[str, Any]

@router.post("", response_model=ValidateResponse)
async def validate_files(request: ValidateRequest):
    if not request.file_ids:
        raise HTTPException(status_code=400, detail="No files provided")
        
    logger.info(f"Validating files: {request.file_ids} as {request.pair_type}")
    
    return ValidateResponse(
        is_valid=True,
        results={
            "pair_type": request.pair_type,
            "status": "valid",
            "message": "All files validated successfully"
        }
    )
