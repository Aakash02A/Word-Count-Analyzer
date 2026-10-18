import logging
from typing import Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import sanitize_filename
from app.db.session import get_db_optional
from app.schemas.analysis import AnalysisRequest, AnalysisResponse, UrlAnalysisRequest
from app.services.analyzer import TextAnalyzer
from app.services.document_service import DocumentExtractionError, document_service
from app.services.history_service import history_service
from app.services.ocr_service import ocr_service
from app.services.url_service import URLExtractionError, url_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/analysis",
    response_model=AnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze raw text",
    description="Calculates word frequencies, token counts, word-length distribution, bigrams, and NLP sentiment.",
)
def analyze_text(
    request: AnalysisRequest,
    db: Optional[Session] = Depends(get_db_optional),
) -> AnalysisResponse:
    """
    Analyzes submitted raw text and produces deterministic word-level analytics and NLP insights.
    """
    raw_text = request.text

    # Validation: empty or whitespace-only input
    if not raw_text or not raw_text.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Input text cannot be empty or whitespace-only.",
        )

    # Validation: input text exceeding configured maximum length
    if len(raw_text) > settings.MAX_TEXT_LENGTH_CHARS:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Input text exceeds maximum allowed size of {settings.MAX_TEXT_LENGTH_CHARS} characters.",
        )

    response = TextAnalyzer.analyze(
        text=raw_text,
        top_n=request.top_n,
        case_sensitive=request.case_sensitive,
        engine=request.engine,
        source_type="text",
    )

    if db is not None and settings.ENABLE_DATABASE_HISTORY:
        try:
            history_service.save_analysis(
                db=db,
                response=response,
                source_type="text",
                source_name="Manual Input",
                engine=request.engine,
                case_sensitive=request.case_sensitive,
                top_n=request.top_n,
            )
        except Exception as e:
            logger.warning("Could not persist text analysis to database history: %s", e)

    return response


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
    db: Optional[Session] = Depends(get_db_optional),
) -> AnalysisResponse:
    """
    Validates uploaded file, extracts plain text, and runs the analytics pipeline.
    """
    filename = sanitize_filename(file.filename or "unknown")

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
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Uploaded file exceeds maximum limit of {max_mb} MB.",
        )

    try:
        extracted_text = document_service.extract_text_from_file(filename, content_bytes)
    except DocumentExtractionError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )

    response = TextAnalyzer.analyze(
        text=extracted_text,
        top_n=top_n,
        case_sensitive=case_sensitive,
        engine=engine,
        source_type="file",
        source_name=filename,
    )

    if db is not None and settings.ENABLE_DATABASE_HISTORY:
        try:
            history_service.save_analysis(
                db=db,
                response=response,
                source_type="file",
                source_name=filename,
                engine=engine,
                case_sensitive=case_sensitive,
                top_n=top_n,
            )
        except Exception as e:
            logger.warning("Could not persist file analysis to database history: %s", e)

    return response


@router.post(
    "/analysis/url",
    response_model=AnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze public webpage",
    description="Fetches webpage content with SSRF protections, extracts text, and runs analytics.",
)
def analyze_url(
    request: UrlAnalysisRequest,
    db: Optional[Session] = Depends(get_db_optional),
) -> AnalysisResponse:
    """
    Safely retrieves content from an external public URL and performs text analysis.
    """
    try:
        extracted_text = url_service.fetch_webpage_text(request.url)
    except URLExtractionError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )

    response = TextAnalyzer.analyze(
        text=extracted_text,
        top_n=request.top_n,
        case_sensitive=request.case_sensitive,
        engine=request.engine,
        source_type="url",
        source_name=request.url,
    )

    if db is not None and settings.ENABLE_DATABASE_HISTORY:
        try:
            history_service.save_analysis(
                db=db,
                response=response,
                source_type="url",
                source_name=request.url,
                engine=request.engine,
                case_sensitive=request.case_sensitive,
                top_n=request.top_n,
            )
        except Exception as e:
            logger.warning("Could not persist URL analysis to database history: %s", e)

    return response


@router.post(
    "/analysis/image",
    response_model=AnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Extract text from image and analyze",
    description="Validates an image file (PNG, JPG, WEBP), performs Tesseract OCR text extraction, and processes linguistic statistics.",
)
async def analyze_image(
    file: UploadFile = File(..., description="Image file (.png, .jpg, .jpeg, .webp)"),
    top_n: int = Form(default=10, ge=1, le=100),
    case_sensitive: bool = Form(default=False),
    engine: str = Form(default="python"),
    db: Optional[Session] = Depends(get_db_optional),
) -> AnalysisResponse:
    """
    Validates uploaded image, extracts printed text via Tesseract OCR, and executes the analytics pipeline.
    """
    filename = sanitize_filename(file.filename or "uploaded_image.png")

    try:
        content_bytes = await file.read()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to read uploaded image file: {str(e)}",
        )

    # File upload size validation
    if len(content_bytes) > settings.MAX_UPLOAD_SIZE_BYTES:
        max_mb = settings.MAX_UPLOAD_SIZE_BYTES // (1024 * 1024)
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Uploaded image exceeds maximum limit of {max_mb} MB.",
        )

    extracted_text, ocr_meta = ocr_service.extract_text(content_bytes, filename)

    response = TextAnalyzer.analyze(
        text=extracted_text,
        top_n=top_n,
        case_sensitive=case_sensitive,
        engine=engine,
        source_type="image",
        source_name=filename,
    )

    # Attach OCR-specific metadata and extracted text preview
    response.extracted_text = extracted_text
    response.metadata.ocr_metadata = ocr_meta

    if db is not None and settings.ENABLE_DATABASE_HISTORY:
        try:
            history_service.save_analysis(
                db=db,
                response=response,
                source_type="image",
                source_name=filename,
                engine=engine,
                case_sensitive=case_sensitive,
                top_n=top_n,
            )
        except Exception as e:
            logger.warning("Could not persist image analysis to database history: %s", e)

    return response

