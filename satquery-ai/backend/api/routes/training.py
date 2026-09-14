import uuid
from typing import List, Dict, Any
from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
from loguru import logger

router = APIRouter(prefix="/training", tags=["Training"])

class PrepareRequest(BaseModel):
    dataset: str

class StartJobRequest(BaseModel):
    dataset: str
    method: str
    epochs: int
    lr: float
    batch_size: int
    adapter_type: str
    device: str

class JobStatus(BaseModel):
    job_id: str
    status: str
    logs: List[str]

JOBS: Dict[str, Dict[str, Any]] = {}

def mock_training_task(job_id: str, request: StartJobRequest):
    logger.info(f"Starting training job {job_id} for {request.dataset}")
    JOBS[job_id]["status"] = "running"
    # Mock progress
    JOBS[job_id]["logs"].append("Training started...")
    JOBS[job_id]["status"] = "completed"
    JOBS[job_id]["logs"].append("Training completed.")

@router.post("/prepare")
async def prepare_training(request: PrepareRequest):
    return {"status": "ready", "message": f"Dataset {request.dataset} prepared or requires data."}

@router.post("/start")
async def start_training(request: StartJobRequest, background_tasks: BackgroundTasks):
    if request.dataset != "BigEarthNet":
        return {"error": "BigEarthNet data is needed first."}
        
    job_id = str(uuid.uuid4())
    JOBS[job_id] = {"status": "pending", "logs": [], "config": request.dict()}
    
    background_tasks.add_task(mock_training_task, job_id, request)
    return {"job_id": job_id, "status": "started"}

@router.get("/status/{job_id}", response_model=JobStatus)
async def get_training_status(job_id: str):
    if job_id not in JOBS:
        raise HTTPException(status_code=404, detail="Job not found")
    job = JOBS[job_id]
    return JobStatus(job_id=job_id, status=job["status"], logs=job["logs"])

@router.get("/jobs")
async def list_jobs():
    return [{"job_id": k, "status": v["status"]} for k, v in JOBS.items()]
