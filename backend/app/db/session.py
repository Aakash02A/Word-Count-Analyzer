import logging
import time
from typing import Any, Dict, Generator, Optional
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings

logger = logging.getLogger(__name__)

engine = None
SessionLocal = None

try:
    engine = create_engine(
        settings.database_url,
        pool_pre_ping=settings.DATABASE_POOL_PRE_PING,
        pool_size=settings.DATABASE_POOL_SIZE,
        max_overflow=settings.DATABASE_MAX_OVERFLOW,
        echo=False,
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    logger.info("SQLAlchemy database engine successfully configured.")
except Exception as e:
    logger.error("Failed to initialize SQLAlchemy database engine: %s", e)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides an isolated database session per request,
    guaranteeing proper closure in a finally block without catching HTTPExceptions.
    """
    if SessionLocal is None:
        raise RuntimeError("Database engine is not initialized.")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_optional() -> Generator[Optional[Session], None, None]:
    """
    FastAPI dependency that yields a database session if configured, or None if disabled,
    ensuring standard exception propagation during HTTP errors.
    """
    if SessionLocal is None or not settings.ENABLE_DATABASE_HISTORY:
        yield None
        return
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db_connectivity() -> Dict[str, Any]:
    """
    Performs an active ping check on MySQL to evaluate connection status and latency.
    Used by readiness endpoints and diagnostics without impacting basic liveness.
    """
    if engine is None:
        return {
            "connected": False,
            "latency_ms": None,
            "database": settings.MYSQL_DB,
            "error": "Engine initialization failure.",
        }

    start = time.perf_counter()
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        latency_ms = round((time.perf_counter() - start) * 1000, 2)
        return {
            "connected": True,
            "latency_ms": latency_ms,
            "database": settings.MYSQL_DB,
            "error": None,
        }
    except Exception as e:
        latency_ms = round((time.perf_counter() - start) * 1000, 2)
        return {
            "connected": False,
            "latency_ms": latency_ms,
            "database": settings.MYSQL_DB,
            "error": str(e),
        }
