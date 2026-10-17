from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import analysis, health
from app.core.config import settings


def create_application() -> FastAPI:
    """Application factory for Word Intelligence FastAPI backend."""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url=f"{settings.API_V1_STR}/docs",
        redoc_url=f"{settings.API_V1_STR}/redoc",
    )

    # Configure CORS
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
    app.include_router(analysis.router, prefix=settings.API_V1_STR, tags=["Analysis"])

    @app.get("/", include_in_schema=False)
    def root():
        return {
            "app": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "docs": f"{settings.API_V1_STR}/docs",
            "health": "/health",
        }

    return app


app = create_application()
