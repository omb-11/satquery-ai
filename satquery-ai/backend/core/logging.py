"""
SatQuery AI — Logging Configuration
"""
import sys
from loguru import logger
from backend.core.config import settings


def setup_logging():
    logger.remove()
    fmt = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "{message}"
    )
    logger.add(sys.stderr, format=fmt, level="DEBUG" if settings.debug else "INFO",
               colorize=True)
    log_file = settings.data_dir / "satquery.log"
    logger.add(str(log_file), format=fmt, level="DEBUG", rotation="10 MB",
               retention="7 days", compression="zip")
    return logger
