import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    DateTime,
    Text,
    Index,
)
from app.db.base import Base


class AnalysisHistory(Base):
    """
    Persisted record of an analysis execution, storing metadata, key indexing metrics,
    and the full structured analytics result for historical review and replaying.
    """
    __tablename__ = "analysis_history"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    source_type = Column(String(20), nullable=False, index=True)  # 'text', 'file', 'url'
    source_name = Column(String(255), nullable=True)  # sanitized label, filename, or url
    engine = Column(String(20), nullable=False, default="python", index=True)  # 'python' or 'pyspark'
    case_sensitive = Column(Boolean, nullable=False, default=False)
    top_n = Column(Integer, nullable=False, default=10)

    # Core scalar metrics for fast querying, filtering, and aggregation
    total_words = Column(Integer, nullable=False, index=True)
    unique_words = Column(Integer, nullable=False)
    avg_word_length = Column(Float, nullable=False)

    # NLP sentiment fields
    sentiment_label = Column(String(20), nullable=True, index=True)  # 'positive', 'neutral', 'negative'
    sentiment_polarity = Column(Float, nullable=True)
    sentiment_subjectivity = Column(Float, nullable=True)

    processing_time_ms = Column(Integer, nullable=True)

    # Serialized complete analysis result payload for full UI reconstruction
    result_json = Column(Text, nullable=False)

    # Timestamp
    created_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )

    __table_args__ = (
        Index("ix_analysis_history_source_engine", "source_type", "engine"),
        Index("ix_analysis_history_created_sentiment", "created_at", "sentiment_label"),
    )

    def get_parsed_result(self) -> Dict[str, Any]:
        """Deserializes stored JSON analysis result."""
        try:
            return json.loads(self.result_json) if self.result_json else {}
        except Exception:
            return {}

    def to_summary_dict(self) -> Dict[str, Any]:
        """Provides a lightweight summary dictionary for listing in tables without transferring large payload."""
        return {
            "id": self.id,
            "source_type": self.source_type,
            "source_name": self.source_name or "Manual Input",
            "engine": self.engine,
            "case_sensitive": self.case_sensitive,
            "top_n": self.top_n,
            "total_words": self.total_words,
            "unique_words": self.unique_words,
            "avg_word_length": round(self.avg_word_length, 2),
            "sentiment_label": self.sentiment_label,
            "sentiment_polarity": round(self.sentiment_polarity, 3) if self.sentiment_polarity is not None else None,
            "sentiment_subjectivity": round(self.sentiment_subjectivity, 3) if self.sentiment_subjectivity is not None else None,
            "processing_time_ms": self.processing_time_ms,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def to_detail_dict(self) -> Dict[str, Any]:
        """Provides full record representation including deserialized result payload."""
        summary = self.to_summary_dict()
        summary["result"] = self.get_parsed_result()
        return summary
