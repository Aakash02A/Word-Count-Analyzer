"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class InputTypeEnum(str, Enum):
    file = "file"
    url = "url"

class StatusEnum(str, Enum):
    processing = "processing"
    completed = "completed"
    failed = "failed"

class JobStatusEnum(str, Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"

# Request Schemas
class FileAnalysisRequest(BaseModel):
    """Schema for file upload request"""
    input_type: str = "file"

class URLAnalysisRequest(BaseModel):
    """Schema for URL analysis request"""
    url: str = Field(..., description="URL to analyze")
    timeout: int = 30

class SparkJobRequest(BaseModel):
    """Schema for Spark job submission"""
    analysis_id: str
    input_type: str
    text: str

class HistoryFilterRequest(BaseModel):
    """Schema for history filtering"""
    input_type: Optional[str] = None
    status: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    skip: int = 0
    limit: int = 50

# Response Schemas
class AnalysisCreate(BaseModel):
    """Analysis creation schema"""
    input_type: str
    input_metadata: Dict[str, Any]
    status: str = "processing"

class AnalysisResponse(BaseModel):
    """Analysis response schema"""
    id: str
    input_type: str
    input_metadata: Dict[str, Any]
    status: str
    raw_data: Optional[str] = None
    processed_data: Optional[Dict[str, Any]] = None
    visualization_data: Optional[Dict[str, Any]] = None
    execution_time: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class SparkJobResponse(BaseModel):
    """Spark job response schema"""
    id: str
    analysis_id: str
    job_id: str
    status: str
    metrics: Optional[Dict[str, Any]] = None
    logs: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class DashboardSummary(BaseModel):
    """Dashboard summary schema"""
    total_analyses: int
    total_files: int
    total_urls: int
    avg_execution_time: float
    recent_analyses: List[AnalysisResponse]
    spark_status: Dict[str, Any]

class VisualizationData(BaseModel):
    """Visualization data schema"""
    word_frequency: Dict[str, Any]
    word_length_histogram: Dict[str, Any]
    sentiment_pie: Dict[str, Any]
    top_bigrams: Dict[str, Any]
    trigrams: Dict[str, Any]
    statistics: Dict[str, Any]

class HistoryItem(BaseModel):
    """Single history item"""
    id: str
    input_type: str
    input_metadata: Dict[str, Any]
    status: str
    execution_time: Optional[float]
    created_at: datetime

class HistoryResponse(BaseModel):
    """History list response"""
    items: List[HistoryItem]
    total: int
    skip: int
    limit: int

class ErrorResponse(BaseModel):
    """Error response schema"""
    detail: str
    status_code: int
