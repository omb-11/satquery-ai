"""
SatQuery AI — Database Setup
"""
from __future__ import annotations
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, Text, DateTime, JSON, Boolean
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from backend.core.config import settings

Base = declarative_base()


class Run(Base):
    __tablename__ = "runs"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    query = Column(Text, nullable=False)
    input_mode = Column(String, nullable=False)  # single | bitemporal | optical_sar
    task_type = Column(String)
    status = Column(String, default="running")  # running | complete | error
    answer = Column(Text)
    confidence_score = Column(Float)
    confidence_level = Column(String)
    models_used = Column(JSON)
    trace = Column(JSON)
    evidence = Column(JSON)
    findings = Column(JSON)
    parameters = Column(JSON)
    limitations = Column(JSON)
    processing_times = Column(JSON)
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)


class InputFile(Base):
    __tablename__ = "input_files"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id = Column(String, nullable=False)
    filename = Column(String, nullable=False)
    stored_path = Column(String, nullable=False)
    file_hash = Column(String)
    file_size_mb = Column(Float)
    modality = Column(String)
    has_crs = Column(Boolean)
    width = Column(Integer)
    height = Column(Integer)
    band_count = Column(Integer)
    crs = Column(String)
    metadata_json = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)


class ModelExecution(Base):
    __tablename__ = "model_executions"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id = Column(String, nullable=False)
    model_name = Column(String)
    tool_name = Column(String)
    elapsed_ms = Column(Float)
    input_params = Column(JSON)
    output_summary = Column(Text)
    status = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


class BenchmarkRun(Base):
    __tablename__ = "benchmark_runs"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    dataset = Column(String)
    task = Column(String)
    total_samples = Column(Integer)
    processed = Column(Integer)
    metrics = Column(JSON)
    status = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


class TrainingJob(Base):
    __tablename__ = "training_jobs"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    dataset = Column(String)
    method = Column(String)
    config = Column(JSON)
    status = Column(String)
    logs = Column(Text)
    epochs_done = Column(Integer, default=0)
    final_loss = Column(Float)
    adapter_path = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)


engine = create_async_engine(settings.database_url, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db():
    """Initialize database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    """FastAPI dependency: provide DB session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
