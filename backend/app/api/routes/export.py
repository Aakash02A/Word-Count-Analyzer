from fastapi import APIRouter, Response, status
from app.schemas.analysis import AnalysisResponse
from app.services.export_service import export_service

router = APIRouter()


@router.post(
    "/export/csv",
    summary="Export analysis as CSV",
    description="Generates an RFC 4180 CSV document with formula injection mitigations.",
    status_code=status.HTTP_200_OK,
    responses={
        200: {
            "content": {"text/csv": {}},
            "description": "Downloadable CSV analysis report",
        }
    },
)
def export_analysis_csv(analysis: AnalysisResponse) -> Response:
    """
    Exports structured analytical results to a sanitized CSV file.
    """
    csv_content = export_service.generate_analysis_csv(analysis)
    return Response(
        content=csv_content,
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": 'attachment; filename="word_intelligence_analysis.csv"',
            "Content-Type": "text/csv; charset=utf-8",
        },
    )
