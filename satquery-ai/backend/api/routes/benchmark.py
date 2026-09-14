from typing import List
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/benchmark", tags=["Benchmark"])

class BenchmarkRunRequest(BaseModel):
    dataset: str
    task: str
    sample_limit: int

@router.post("/run")
async def run_benchmark(request: BenchmarkRunRequest):
    return {
        "status": "not_evaluated",
        "message": f"Benchmark for {request.dataset} on {request.task} not yet evaluated."
    }

@router.get("/datasets", response_model=List[str])
async def list_datasets():
    return ["BigEarthNet", "EuroSAT", "RESISC45"]
