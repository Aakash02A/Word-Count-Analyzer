import io
import os
import shutil
from typing import Dict, Any, Tuple, Optional
from PIL import Image, ImageEnhance, ImageOps
import pytesseract
from fastapi import HTTPException, status
from app.core.config import settings

# Enforce decompression bomb limits
Image.MAX_IMAGE_PIXELS = settings.MAX_IMAGE_PIXELS

SUPPORTED_IMAGE_FORMATS = {"PNG", "JPEG", "JPG", "WEBP"}
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}


def get_tesseract_binary() -> Optional[str]:
    """
    Discovers the Tesseract binary across explicit configuration,
    environment variables, system PATH, and standard OS directories.
    """
    # 1. Configured via application settings
    if settings.TESSERACT_CMD and os.path.isfile(settings.TESSERACT_CMD):
        return settings.TESSERACT_CMD

    # 2. Environment variable
    env_cmd = os.environ.get("TESSERACT_CMD")
    if env_cmd and os.path.isfile(env_cmd):
        return env_cmd

    # 3. System PATH lookup
    path_which = shutil.which("tesseract")
    if path_which:
        return path_which

    # 4. Standard platform installation locations
    candidate_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Tesseract-OCR\tesseract.exe"),
        "/usr/bin/tesseract",
        "/usr/local/bin/tesseract",
    ]

    for p in candidate_paths:
        if os.path.isfile(p):
            return p

    return None


class OCRService:
    """
    Validates, preprocesses, and extracts text from uploaded images using Tesseract OCR.
    """

    def __init__(self):
        self._tesseract_cmd = get_tesseract_binary()
        if self._tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = self._tesseract_cmd

    def is_available(self) -> bool:
        """Checks if Tesseract binary is available on the host."""
        if not self._tesseract_cmd:
            self._tesseract_cmd = get_tesseract_binary()
            if self._tesseract_cmd:
                pytesseract.pytesseract.tesseract_cmd = self._tesseract_cmd
        return self._tesseract_cmd is not None

    def validate_and_preprocess_image(self, file_bytes: bytes, filename: str) -> Tuple[Image.Image, Dict[str, Any]]:
        """
        Validates image content, checks dimensions and limits, and applies grayscale/contrast preprocessing.
        """
        # Extension check
        ext = os.path.splitext(filename.lower())[1]
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported image file extension '{ext}'. Permitted formats: PNG, JPG, JPEG, WEBP."
            )

        # Upload size check
        if len(file_bytes) > settings.MAX_UPLOAD_SIZE_BYTES:
            max_mb = settings.MAX_UPLOAD_SIZE_BYTES // (1024 * 1024)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Image upload exceeds maximum allowed size of {max_mb} MB."
            )

        if not file_bytes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded image file is empty."
            )

        # Pillow load and format verification
        try:
            raw_img = Image.open(io.BytesIO(file_bytes))
            raw_img.load()  # Force load pixel data to detect corruption
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Corrupted, unreadable, or invalid image file."
            )

        detected_format = (raw_img.format or "").upper()
        if detected_format not in SUPPORTED_IMAGE_FORMATS and ext.lstrip(".").upper() not in SUPPORTED_IMAGE_FORMATS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported image format '{detected_format}'. Supported formats: PNG, JPEG, WEBP."
            )

        width, height = raw_img.size
        total_pixels = width * height
        if total_pixels > settings.MAX_IMAGE_PIXELS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Image dimensions ({width}x{height}) exceed maximum allowed total pixels ({settings.MAX_IMAGE_PIXELS})."
            )

        # Preprocessing: convert to RGB/L, auto-orient from EXIF, enhance contrast
        try:
            # Handle EXIF orientation
            oriented_img = ImageOps.exif_transpose(raw_img)
            if oriented_img is None:
                oriented_img = raw_img

            # Convert to grayscale for OCR accuracy
            gray = oriented_img.convert("L")

            # Mild contrast enhancement to sharpen text boundaries
            enhancer = ImageEnhance.Contrast(gray)
            processed_img = enhancer.enhance(1.4)
        except Exception:
            # Fall back to raw image if preprocessing fails
            processed_img = raw_img

        metadata = {
            "format": detected_format or ext.lstrip(".").upper(),
            "dimensions": f"{width}x{height}",
            "width": width,
            "height": height,
            "preprocessed": True,
        }
        return processed_img, metadata

    def extract_text(self, file_bytes: bytes, filename: str) -> Tuple[str, Dict[str, Any]]:
        """
        Extracts readable text from an image with full safety validation, preprocessing, and OCR.
        """
        processed_img, metadata = self.validate_and_preprocess_image(file_bytes, filename)

        if not self.is_available():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Tesseract OCR engine is not installed or not found on this system. "
                       "Please install Tesseract or configure TESSERACT_CMD."
            )

        try:
            text = pytesseract.image_to_string(
                processed_img,
                timeout=settings.OCR_TIMEOUT_SECONDS,
                lang="eng",
            )
        except pytesseract.TesseractNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Tesseract OCR executable not found on host system."
            )
        except RuntimeError as e:
            if "timeout" in str(e).lower():
                raise HTTPException(
                    status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                    detail=f"OCR processing timed out after {settings.OCR_TIMEOUT_SECONDS} seconds."
                )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"OCR processing failure: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to extract text from image: {str(e)}"
            )

        cleaned_text = (text or "").strip()
        if not cleaned_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No readable printed text could be extracted from the uploaded image."
            )

        if len(cleaned_text) > settings.MAX_TEXT_LENGTH_CHARS:
            cleaned_text = cleaned_text[: settings.MAX_TEXT_LENGTH_CHARS]

        metadata["ocr_engine"] = "tesseract"
        metadata["ocr_chars_extracted"] = len(cleaned_text)
        return cleaned_text, metadata


# Global singleton instance
ocr_service = OCRService()
