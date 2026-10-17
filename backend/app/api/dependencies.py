"""API dependency injection utilities."""
from app.core.config import Settings, settings


def get_settings() -> Settings:
    """Dependency provider for application settings."""
    return settings
