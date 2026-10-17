from fastapi import APIRouter, HTTPException, status
from app.core.config import settings
from app.schemas.analysis import AnalysisRequest, AnalysisResponse
from app.services.analyzer import TextAnalyzer

router = APIRouter()


@router.post(
    "/analysis",
    response_model=AnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze raw text",
    description="Calculates word frequencies, token counts, word-length distribution, and common bigrams.",
)
def analyze_text(request: AnalysisRequest) -> AnalysisResponse:
    """
    Analyzes submitted raw text and produces deterministic word-level analytics.
    """
    raw_text = request.text

    # Validation: empty or whitespace-only input
    if not raw_text or not raw_text.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Input text cannot be empty or whitespace-only.",
        )

    # Validation: input text exceeding configured maximum length
    if len(raw_text) > settings.MAX_TEXT_LENGTH_CHARS:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=f"Input text exceeds maximum allowed size of {settings.MAX_TEXT_LENGTH_CHARS} characters.",
        )

    response = TextAnalyzer.analyze(
        text=raw_text,
        top_n=request.top_n,
        case_sensitive=request.case_sensitive,
    )

    return response
