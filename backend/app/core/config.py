import json
from typing import List, Optional, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    ENVIRONMENT: str = "development"
    PROJECT_NAME: str = "Word Intelligence"
    VERSION: str = "0.4.0"
    API_V1_STR: str = "/api/v1"

    BACKEND_HOST: str = "127.0.0.1"
    BACKEND_PORT: int = 8000

    BACKEND_CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [i.strip() for i in v.split(",") if i.strip()]
        return v

    MAX_UPLOAD_SIZE_BYTES: int = 10 * 1024 * 1024  # 10 MB
    MAX_TEXT_LENGTH_CHARS: int = 500000
    HTTP_REQUEST_TIMEOUT_SECONDS: int = 10

    # OCR Image Configuration (Section 21)
    TESSERACT_CMD: Optional[str] = None
    MAX_IMAGE_PIXELS: int = 25_000_000  # 25 Megapixels
    OCR_TIMEOUT_SECONDS: int = 20

    # Apache PySpark configuration
    SPARK_MASTER: str = "local[2]"
    SPARK_APP_NAME: str = "WordIntelligence"
    SPARK_UI_ENABLED: bool = False
    SPARK_DRIVER_MEMORY: str = "1g"
    ENABLE_SPARK_ANALYTICS: bool = True

    # MySQL Database configuration (Phase 6)
    MYSQL_SERVER: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = ""
    MYSQL_DB: str = "word_intelligence"
    SQLALCHEMY_DATABASE_URI: Optional[str] = None
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10
    DATABASE_POOL_PRE_PING: bool = True
    ENABLE_DATABASE_HISTORY: bool = True

    # Security & Abuse Prevention (Phase 7)
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 120

    @property
    def database_url(self) -> str:
        if self.SQLALCHEMY_DATABASE_URI:
            uri = self.SQLALCHEMY_DATABASE_URI
            if "${" in uri:
                uri = (
                    uri.replace("${MYSQL_USER}", self.MYSQL_USER)
                    .replace("${MYSQL_PASSWORD}", self.MYSQL_PASSWORD)
                    .replace("${MYSQL_SERVER}", self.MYSQL_SERVER)
                    .replace("${MYSQL_PORT}", str(self.MYSQL_PORT))
                    .replace("${MYSQL_DB}", self.MYSQL_DB)
                )
            if "charset=" not in uri:
                sep = "&" if "?" in uri else "?"
                uri = f"{uri}{sep}charset=utf8mb4"
            return uri
        return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_SERVER}:{self.MYSQL_PORT}/{self.MYSQL_DB}?charset=utf8mb4"


settings = Settings()
