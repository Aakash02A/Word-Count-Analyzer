from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import analysis, export, health, history, readiness
from app.core.config import settings
from app.core.security import RateLimitMiddleware, SecurityHeadersMiddleware
from app.services.spark_service import spark_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan managing external services including PySpark."""
    yield
    # Graceful shutdown of PySpark session
    spark_service.stop_session()


def create_application() -> FastAPI:
    """Application factory for Word Intelligence FastAPI backend."""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url=f"{settings.API_V1_STR}/docs",
        redoc_url=f"{settings.API_V1_STR}/redoc",
        lifespan=lifespan,
    )

    # Security Headers Middleware
    app.add_middleware(SecurityHeadersMiddleware)

    # Sliding Window Rate Limiting Middleware
    app.add_middleware(RateLimitMiddleware)

    # Configure CORS with strict origin handling
    origins = [str(origin).rstrip("/") for origin in settings.BACKEND_CORS_ORIGINS]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Root health endpoint (for liveness probes)
    app.include_router(health.router, tags=["Health"])

    # Versioned API prefix endpoints
    app.include_router(health.router, prefix=settings.API_V1_STR, tags=["Health"])
    app.include_router(readiness.router, prefix=settings.API_V1_STR, tags=["Health"])
    app.include_router(analysis.router, prefix=settings.API_V1_STR, tags=["Analysis"])
    app.include_router(export.router, prefix=settings.API_V1_STR, tags=["Export"])
    app.include_router(history.router, prefix=settings.API_V1_STR, tags=["History"])

    @app.get("/", include_in_schema=False)
    def root():
        return {
            "app": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "docs": f"{settings.API_V1_STR}/docs",
            "health": "/health",
            "readiness": f"{settings.API_V1_STR}/readiness",
        }

    return app


app = create_application()
