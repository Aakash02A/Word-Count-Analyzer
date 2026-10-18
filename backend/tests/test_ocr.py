import io
from unittest.mock import patch
import pytest
from PIL import Image, ImageDraw
from fastapi.testclient import TestClient
from fastapi import HTTPException

from app.main import app
from app.services.ocr_service import OCRService, ocr_service
from app.core.config import settings


@pytest.fixture
def client():
    return TestClient(app)


def create_test_image_bytes(text: str = "Hello World", size=(200, 80), format: str = "PNG") -> bytes:
    """Helper creating an in-memory test image with synthetic text."""
    img = Image.new("RGB", size, color="white")
    draw = ImageDraw.Draw(img)
    draw.text((10, 30), text, fill="black")
    buf = io.BytesIO()
    img.save(buf, format=format)
    return buf.getvalue()


class TestOCRValidation:
    """Unit tests for OCR image validation, dimension checking, and preprocessing."""

    def test_empty_image_bytes_rejected(self):
        service = OCRService()
        with pytest.raises(HTTPException) as exc:
            service.validate_and_preprocess_image(b"", "test.png")
        assert exc.value.status_code == 400
        assert "empty" in exc.value.detail.lower()

    def test_unsupported_extension_rejected(self):
        service = OCRService()
        with pytest.raises(HTTPException) as exc:
            service.validate_and_preprocess_image(b"fakebytes", "test.gif")
        assert exc.value.status_code == 400
        assert "unsupported" in exc.value.detail.lower()

    def test_corrupted_image_rejected(self):
        service = OCRService()
        with pytest.raises(HTTPException) as exc:
            service.validate_and_preprocess_image(b"corrupted raw data not an image", "test.png")
        assert exc.value.status_code == 400
        assert "corrupted" in exc.value.detail.lower() or "invalid" in exc.value.detail.lower()

    def test_valid_image_preprocessing(self):
        service = OCRService()
        valid_png = create_test_image_bytes("Sample Text", size=(150, 60), format="PNG")
        processed_img, meta = service.validate_and_preprocess_image(valid_png, "sample.png")

        assert processed_img is not None
        assert processed_img.mode == "L"  # Converted to grayscale for OCR
        assert meta["format"] == "PNG"
        assert meta["dimensions"] == "150x60"
        assert meta["preprocessed"] is True

    def test_dimension_limits_rejected(self):
        service = OCRService()
        # Create a tiny 1x1 image, but test against a very small MAX_IMAGE_PIXELS setting
        test_png = create_test_image_bytes("test", size=(50, 50), format="PNG")
        with patch.object(settings, "MAX_IMAGE_PIXELS", 100):
            with pytest.raises(HTTPException) as exc:
                service.validate_and_preprocess_image(test_png, "huge.png")
            assert exc.value.status_code == 400
            assert "exceed maximum allowed" in exc.value.detail.lower()


class TestOCRExtraction:
    """Tests for OCR execution, error states, and text extraction."""

    def test_ocr_missing_executable_error(self):
        service = OCRService()
        valid_png = create_test_image_bytes("Test Text")

        with patch.object(service, "is_available", return_value=False):
            with pytest.raises(HTTPException) as exc:
                service.extract_text(valid_png, "test.png")
            assert exc.value.status_code == 503
            assert "tesseract ocr engine is not installed" in exc.value.detail.lower()

    def test_ocr_empty_extracted_text_error(self):
        service = OCRService()
        valid_png = create_test_image_bytes("Blanks")

        with patch.object(service, "is_available", return_value=True), \
             patch("pytesseract.image_to_string", return_value="   \n\t  "):
            with pytest.raises(HTTPException) as exc:
                service.extract_text(valid_png, "blank.png")
            assert exc.value.status_code == 400
            assert "no readable printed text" in exc.value.detail.lower()

    def test_ocr_successful_text_extraction(self):
        service = OCRService()
        valid_png = create_test_image_bytes("Artificial Intelligence")

        sample_extracted = "Artificial Intelligence and Big Data Analytics"
        with patch.object(service, "is_available", return_value=True), \
             patch("pytesseract.image_to_string", return_value=sample_extracted):
            extracted, meta = service.extract_text(valid_png, "ai_doc.png")

            assert extracted == sample_extracted
            assert meta["ocr_engine"] == "tesseract"
            assert meta["ocr_chars_extracted"] == len(sample_extracted)


class TestImageAnalysisEndpoint:
    """Integration tests for POST /api/v1/analysis/image."""

    def test_image_analysis_endpoint_invalid_file(self, client):
        response = client.post(
            "/api/v1/analysis/image",
            files={"file": ("invalid.txt", b"plain text content", "text/plain")},
        )
        assert response.status_code == 400
        assert "unsupported image" in response.json()["detail"].lower()

    def test_image_analysis_endpoint_success(self, client):
        valid_png = create_test_image_bytes("FastAPI PySpark NLP")
        extracted_mock = "FastAPI and Apache PySpark analytics with NLP"

        with patch.object(ocr_service, "is_available", return_value=True), \
             patch("pytesseract.image_to_string", return_value=extracted_mock):
            response = client.post(
                "/api/v1/analysis/image",
                files={"file": ("test_page.png", valid_png, "image/png")},
                data={"top_n": "5", "case_sensitive": "false", "engine": "python"},
            )

            assert response.status_code == 200
            data = response.json()
            assert data["total_tokens"] > 0
            assert data["metadata"]["source_type"] == "image"
            assert data["metadata"]["source_name"] == "test_page.png"
            assert data["extracted_text"] == extracted_mock
            assert data["metadata"]["ocr_metadata"]["ocr_engine"] == "tesseract"
