from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class HistorySummaryItem(BaseModel):
    id: int
    source_type: str
    source_name: str
    engine: str
    case_sensitive: bool
    top_n: int
    total_words: int
    unique_words: int
    avg_word_length: float
    sentiment_label: Optional[str] = None
    sentiment_polarity: Optional[float] = None
    sentiment_subjectivity: Optional[float] = None
    processing_time_ms: Optional[int] = None
    created_at: Optional[str] = None


class HistoryListResponse(BaseModel):
    items: List[HistorySummaryItem]
    total: int
    skip: int
    limit: int


class HistoryDetailResponse(HistorySummaryItem):
    result: Dict[str, Any] = Field(..., description="Full structured analysis payload for replaying")


class HistoryStatsResponse(BaseModel):
    total_runs: int
    total_words_analyzed: int
    latest_run_at: Optional[str] = None
