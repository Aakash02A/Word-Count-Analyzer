import json
import logging
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy import or_, desc, func
from sqlalchemy.orm import Session
from app.models.history import AnalysisHistory
from app.schemas.analysis import AnalysisResponse

logger = logging.getLogger(__name__)


class HistoryService:
    """Service handling persistence, querying, and deletion of analysis history records."""

    @staticmethod
    def save_analysis(
        db: Session,
        response: AnalysisResponse,
        source_type: str,
        source_name: Optional[str] = None,
        engine: str = "python",
        case_sensitive: bool = False,
        top_n: int = 10,
        processing_time_ms: Optional[int] = None,
    ) -> AnalysisHistory:
        """
        Extracts metrics and full serialized payload from AnalysisResponse and writes
        an immutable historical record into MySQL within a transaction.
        """
        result_payload = response.model_dump()
        result_json_str = json.dumps(result_payload)

        # Extract sentiment data if present
        sentiment_label = response.sentiment.label if response.sentiment else None
        sentiment_polarity = response.sentiment.polarity if response.sentiment else None
        sentiment_subjectivity = response.sentiment.subjectivity if response.sentiment else None

        exec_time = None
        if response.metadata and response.metadata.execution_time_ms is not None:
            exec_time = int(round(response.metadata.execution_time_ms))
        elif processing_time_ms is not None:
            exec_time = processing_time_ms

        record = AnalysisHistory(
            source_type=source_type,
            source_name=source_name or "Manual Input",
            engine=engine,
            case_sensitive=case_sensitive,
            top_n=top_n,
            total_words=response.total_tokens,
            unique_words=response.unique_tokens,
            avg_word_length=response.average_word_length,
            sentiment_label=sentiment_label,
            sentiment_polarity=sentiment_polarity,
            sentiment_subjectivity=sentiment_subjectivity,
            processing_time_ms=exec_time,
            result_json=result_json_str,
        )

        db.add(record)
        db.commit()
        db.refresh(record)
        logger.info("Successfully persisted analysis run #%s for source %s", record.id, source_type)
        return record

    @staticmethod
    def list_history(
        db: Session,
        skip: int = 0,
        limit: int = 20,
        source_type: Optional[str] = None,
        engine: Optional[str] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[AnalysisHistory], int]:
        """
        Retrieves paginated historical summaries with optional filtering by
        source type, engine, or source name keyword.
        """
        query = db.query(AnalysisHistory)

        if source_type and source_type.lower() != "all":
            query = query.filter(AnalysisHistory.source_type == source_type.lower())

        if engine and engine.lower() != "all":
            query = query.filter(AnalysisHistory.engine == engine.lower())

        if search and search.strip():
            term = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    AnalysisHistory.source_name.ilike(term),
                    AnalysisHistory.sentiment_label.ilike(term),
                )
            )

        total_count = query.count()
        records = (
            query.order_by(desc(AnalysisHistory.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )
        return records, total_count

    @staticmethod
    def get_history_by_id(db: Session, history_id: int) -> Optional[AnalysisHistory]:
        """Retrieves a single historical record by ID."""
        return db.query(AnalysisHistory).filter(AnalysisHistory.id == history_id).first()

    @staticmethod
    def delete_history(db: Session, history_id: int) -> bool:
        """Removes a single history record by ID."""
        record = db.query(AnalysisHistory).filter(AnalysisHistory.id == history_id).first()
        if not record:
            return False
        db.delete(record)
        db.commit()
        logger.info("Deleted analysis history record #%s", history_id)
        return True

    @staticmethod
    def get_stats(db: Session) -> Dict[str, Any]:
        """Aggregates summary statistics over stored history."""
        total_runs = db.query(func.count(AnalysisHistory.id)).scalar() or 0
        total_words_analyzed = db.query(func.sum(AnalysisHistory.total_words)).scalar() or 0
        latest_run = (
            db.query(AnalysisHistory.created_at)
            .order_by(desc(AnalysisHistory.created_at))
            .first()
        )
        return {
            "total_runs": total_runs,
            "total_words_analyzed": int(total_words_analyzed),
            "latest_run_at": latest_run[0].isoformat() if latest_run else None,
        }


history_service = HistoryService()
