from typing import Any, Dict
from fastapi import APIRouter, status
from app.core.config import settings
from app.db.session import check_db_connectivity
from app.services.spark_service import spark_service

router = APIRouter(prefix="/readiness", tags=["System Health & Diagnostics"])


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    summary="Readiness probe",
    description="Evaluates connectivity to backend dependencies (MySQL, Spark) without failing basic liveness.",
)
def get_readiness() -> Dict[str, Any]:
    db_status = check_db_connectivity()
    spark_active = spark_service._session is not None

    all_ready = db_status.get("connected", False)

    return {
        "status": "ready" if all_ready else "degraded",
        "app": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "database": db_status,
        "spark": {
            "configured": settings.ENABLE_SPARK_ANALYTICS,
            "active": spark_active,
            "master": settings.SPARK_MASTER,
        },
    }
