from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.history import (
    HistoryDetailResponse,
    HistoryListResponse,
    HistoryStatsResponse,
    HistorySummaryItem,
)
from app.services.history_service import history_service

router = APIRouter(prefix="/history", tags=["History & Persistence"])


@router.get(
    "",
    response_model=HistoryListResponse,
    status_code=status.HTTP_200_OK,
    summary="List analysis history",
    description="Retrieves a paginated list of past analysis executions with filtering options.",
)
def get_history_list(
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=20, ge=1, le=100, description="Maximum number of records to return"),
    source_type: Optional[str] = Query(default=None, description="Filter by source type ('text', 'file', 'url')"),
    engine: Optional[str] = Query(default=None, description="Filter by engine ('python', 'pyspark')"),
    search: Optional[str] = Query(default=None, description="Search keyword matching source name"),
    db: Session = Depends(get_db),
) -> HistoryListResponse:
    records, total_count = history_service.list_history(
        db=db,
        skip=skip,
        limit=limit,
        source_type=source_type,
        engine=engine,
        search=search,
    )
    items = [HistorySummaryItem(**r.to_summary_dict()) for r in records]
    return HistoryListResponse(items=items, total=total_count, skip=skip, limit=limit)


@router.get(
    "/stats",
    response_model=HistoryStatsResponse,
    status_code=status.HTTP_200_OK,
    summary="History statistics",
    description="Aggregated metadata including total runs, total words analyzed, and latest run timestamp.",
)
def get_history_stats(db: Session = Depends(get_db)) -> HistoryStatsResponse:
    stats = history_service.get_stats(db)
    return HistoryStatsResponse(**stats)


@router.get(
    "/{history_id}",
    response_model=HistoryDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get history record detail",
    description="Fetches full analysis payload for replaying interactive charts and frequency tables.",
)
def get_history_detail(
    history_id: int,
    db: Session = Depends(get_db),
) -> HistoryDetailResponse:
    record = history_service.get_history_by_id(db, history_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"History record #{history_id} not found.",
        )
    return HistoryDetailResponse(**record.to_detail_dict())


@router.delete(
    "/{history_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete history record",
    description="Permanently deletes an analysis history record from the database.",
)
def delete_history_record(
    history_id: int,
    db: Session = Depends(get_db),
) -> dict:
    deleted = history_service.delete_history(db, history_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"History record #{history_id} not found.",
        )
    return {"success": True, "message": f"History record #{history_id} deleted."}
