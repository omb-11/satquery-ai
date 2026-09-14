from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/runs", tags=["Runs"])

class RunBase(BaseModel):
    id: str
    query: str
    status: str
    created_at: str

class RunDetail(RunBase):
    result: Dict[str, Any]
    trace: List[Dict[str, Any]]

@router.get("", response_model=List[RunBase])
async def list_runs():
    return [
        RunBase(id="run-1", query="Detect clouds", status="completed", created_at="2026-09-14T10:00:00Z")
    ]

@router.get("/{run_id}", response_model=RunDetail)
async def get_run(run_id: str):
    if run_id == "run-1":
        return RunDetail(
            id=run_id,
            query="Detect clouds",
            status="completed",
            created_at="2026-09-14T10:00:00Z",
            result={"findings": "No clouds"},
            trace=[{"step": 1, "action": "loaded"}]
        )
    raise HTTPException(status_code=404, detail="Run not found")

@router.get("/{run_id}/trace")
async def get_run_trace(run_id: str):
    if run_id == "run-1":
        return [{"step": 1, "action": "loaded"}]
    raise HTTPException(status_code=404, detail="Run not found")
