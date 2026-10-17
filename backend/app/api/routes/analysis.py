from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from app.core.config import settings
from app.schemas.analysis import AnalysisRequest, AnalysisResponse, UrlAnalysisRequest
from app.services.analyzer import TextAnalyzer
from app.services.document_service import DocumentExtractionError, document_service
from app.services.url_service import URLExtractionError, url_service

router = APIRouter()


@router.post(
    "/analysis",
    response_model=AnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze raw text",
    description="Calculates word frequencies, token counts, word-length distribution, bigrams, and NLP sentiment.",
)
def analyze_text(request: AnalysisRequest) -> AnalysisResponse:
    """
    Analyzes submitted raw text and produces deterministic word-level analytics and NLP insights.
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

    return TextAnalyzer.analyze(
        text=raw_text,
        top_n=request.top_n,
        case_sensitive=request.case_sensitive,
        engine=request.engine,
        source_type="text",
    )


@router.post(
    "/analysis/file",
    response_model=AnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze uploaded document",
    description="Extracts and analyzes text from TXT, PDF, and DOCX files.",
)
async def analyze_file(
    file: UploadFile = File(..., description="Document file (.txt, .pdf, .docx)"),
    top_n: int = Form(default=10, ge=1, le=100),
    case_sensitive: bool = Form(default=False),
    engine: str = Form(default="python"),
) -> AnalysisResponse:
    """
    Validates uploaded file, extracts plain text, and runs the analytics pipeline.
    """
    filename = file.filename or "unknown"

    try:
        content_bytes = await file.read()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to read uploaded file: {str(e)}",
        )

    # Check upload size
    if len(content_bytes) > settings.MAX_UPLOAD_SIZE_BYTES:
        max_mb = settings.MAX_UPLOAD_SIZE_BYTES // (1024 * 1024)
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=f"Uploaded file exceeds maximum limit of {max_mb} MB.",
        )

    try:
        extracted_text = document_service.extract_text_from_file(filename, content_bytes)
    except DocumentExtractionError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(e),
        )

    return TextAnalyzer.analyze(
        text=extracted_text,
        top_n=top_n,
        case_sensitive=case_sensitive,
        engine=engine,
        source_type="file",
        source_name=filename,
    )


@router.post(
    "/analysis/url",
    response_model=AnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze public webpage",
    description="Fetches webpage content with SSRF protections, extracts text, and runs analytics.",
)
def analyze_url(request: UrlAnalysisRequest) -> AnalysisResponse:
    """
    Safely retrieves content from an external public URL and performs text analysis.
    """
    try:
        extracted_text = url_service.fetch_webpage_text(request.url)
    except URLExtractionError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(e),
        )

    return TextAnalyzer.analyze(
        text=extracted_text,
        top_n=request.top_n,
        case_sensitive=request.case_sensitive,
        engine=request.engine,
        source_type="url",
        source_name=request.url,
    )
