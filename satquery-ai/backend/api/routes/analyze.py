"""
SatQuery AI — Analyze Routes
Real analysis using the AgentOrchestrator.
"""
from __future__ import annotations
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Any, Optional

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from backend.core.database import get_db, Run, InputFile
from backend.core.config import settings
from backend.agents.orchestrator import AgentOrchestrator

router = APIRouter()


class AnalyzeRequest(BaseModel):
    query: str
    file_ids: List[str]
    input_mode: str = "single"  # single | bitemporal | optical_sar
    parameters: Optional[dict] = None


async def resolve_paths(file_ids: List[str], db: AsyncSession) -> List[str]:
    """Resolve file_ids to stored paths from DB, demo_data, or upload directory."""
    paths = []
    demo_map = {
        "demo_opt_001": "demo_data/single_optical/scene_optical.tif",
        "demo_sar_001": "demo_data/single_sar/scene_sar.tif",
        "demo_t1_001": "demo_data/temporal/t1_before.tif",
        "demo_t2_001": "demo_data/temporal/t2_after.tif",
        "demo_opt_002": "demo_data/optical_sar/optical.tif",
        "demo_sar_002": "demo_data/optical_sar/sar.tif",
    }
    from sqlalchemy import select
    for fid in file_ids:
        # Check demo presets first
        if fid in demo_map and Path(demo_map[fid]).exists():
            paths.append(str(Path(demo_map[fid]).resolve()))
            continue

        # Try to find in DB
        result = await db.execute(select(InputFile).where(InputFile.id == fid))
        file_record = result.scalar_one_or_none()
        if file_record and Path(file_record.stored_path).exists():
            paths.append(file_record.stored_path)
        else:
            # Try direct path in uploads
            candidate = settings.upload_dir / fid
            if candidate.exists():
                for ext in [".tif", ".tiff", ".png", ".jpg", ".jpeg"]:
                    found = list(candidate.glob(f"*{ext}"))
                    if found:
                        paths.append(str(found[0]))
                        break
            else:
                if Path(fid).exists():
                    paths.append(fid)
    return paths


async def save_run(state, db: AsyncSession):
    """Persist analysis run to database."""
    try:
        run = Run(
            id=state.run_id,
            query=state.query,
            input_mode=state.input_mode,
            task_type=state.task_type,
            status=state.status,
            answer=state.final_answer,
            confidence_score=state.confidence.score if state.confidence else 0,
            confidence_level=state.confidence.level if state.confidence else "low",
            models_used=[m for m in state.models_used],
            trace=[t.to_dict() if hasattr(t, 'to_dict') else t for t in state.trace],
            evidence=[e.to_dict() if hasattr(e, 'to_dict') else e for e in state.evidence],
            findings=state.findings,
            parameters=state.parameters,
            limitations=state.limitations,
            processing_times=state.processing_times,
            error_message=state.error or None,
            created_at=datetime.fromisoformat(state.created_at) if state.created_at else datetime.utcnow(),
            completed_at=datetime.utcnow(),
        )
        db.add(run)
        await db.commit()
    except Exception as e:
        logger.error(f"Failed to save run: {e}")


@router.post("/analyze")
async def analyze_sync(request: AnalyzeRequest, db: AsyncSession = Depends(get_db)):
    """
    Run full agentic analysis synchronously.
    Returns complete result with evidence, trace, and confidence.
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    if not request.file_ids:
        raise HTTPException(status_code=400, detail="At least one file_id is required")

    paths = await resolve_paths(request.file_ids, db)
    if not paths:
        raise HTTPException(
            status_code=400,
            detail="No valid files found for the provided file_ids. Please upload files first.",
        )

    logger.info(f"Analyzing: mode={request.input_mode}, query='{request.query[:60]}', paths={paths}")

    orchestrator = AgentOrchestrator()
    state = await orchestrator.analyze(
        request.query, paths, request.input_mode, parameters=request.parameters
    )

    await save_run(state, db)

    return state.to_dict()


@router.post("/analyze/stream")
async def analyze_stream(request: AnalyzeRequest, db: AsyncSession = Depends(get_db)):
    """
    Stream analysis progress via Server-Sent Events.
    Each event is: data: <JSON>\n\n
    Final event contains the complete result.
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    paths = await resolve_paths(request.file_ids, db)
    if not paths:
        # Allow demo mode with no files
        paths = []

    orchestrator = AgentOrchestrator()

    async def event_generator():
        try:
            async for event_json in orchestrator.analyze_stream(
                request.query, paths, request.input_mode, parameters=request.parameters
            ):
                yield f"data: {event_json}\n\n"

            # Save run after streaming completes (best-effort)
        except Exception as e:
            logger.error(f"Stream error: {e}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/analyze/single")
async def analyze_single(request: AnalyzeRequest, db: AsyncSession = Depends(get_db)):
    """Analyze a single image (alias for /analyze with mode=single)."""
    request.input_mode = "single"
    return await analyze_sync(request, db)


@router.post("/analyze/change")
async def analyze_change(request: AnalyzeRequest, db: AsyncSession = Depends(get_db)):
    """Bi-temporal change analysis (alias for /analyze with mode=bitemporal)."""
    request.input_mode = "bitemporal"
    return await analyze_sync(request, db)


@router.post("/analyze/fusion")
async def analyze_fusion(request: AnalyzeRequest, db: AsyncSession = Depends(get_db)):
    """Optical+SAR fusion analysis (alias for /analyze with mode=optical_sar)."""
    request.input_mode = "optical_sar"
    return await analyze_sync(request, db)


@router.post("/vqa")
async def vqa(request: AnalyzeRequest, db: AsyncSession = Depends(get_db)):
    """Single-image VQA endpoint."""
    request.input_mode = "single"
    return await analyze_sync(request, db)


@router.post("/caption")
async def caption(request: AnalyzeRequest, db: AsyncSession = Depends(get_db)):
    """Scene captioning endpoint."""
    request.query = "Describe this satellite scene in detail."
    request.input_mode = "single"
    return await analyze_sync(request, db)
