from fastapi import APIRouter

from .system import router as system_router
from .upload import router as upload_router
from .validate import router as validate_router
from .analyze import router as analyze_router
from .models import router as models_router
from .runs import router as runs_router
from .reports import router as reports_router
from .benchmark import router as benchmark_router
from .training import router as training_router

router = APIRouter()

router.include_router(system_router)
router.include_router(upload_router)
router.include_router(validate_router)
router.include_router(analyze_router)
router.include_router(models_router)
router.include_router(runs_router)
router.include_router(reports_router)
router.include_router(benchmark_router)
router.include_router(training_router)
