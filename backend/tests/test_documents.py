import io
import pytest
import docx
import pypdf
from fastapi.testclient import TestClient

from app.main import app
from app.services.document_service import DocumentExtractionError, DocumentService


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def create_in_memory_pdf(text: str) -> bytes:
    """Helper creating a minimal valid PDF in memory with text."""
    writer = pypdf.PdfWriter()
    # Add a blank page
    page = writer.add_blank_page(width=200, height=200)
    # Write to buffer
    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()


def create_in_memory_docx(text: str) -> bytes:
    """Helper creating a minimal valid DOCX document in memory."""
    doc = docx.Document()
    doc.add_paragraph(text)
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


def test_document_service_txt_extraction():
    content = "Python and FastAPI text processing.".encode("utf-8")
    extracted = DocumentService.extract_text_from_file("sample.txt", content)
    assert "Python and FastAPI text processing." in extracted


def test_document_service_docx_extraction():
    content = create_in_memory_docx("Word Intelligence DOCX extraction test.")
    extracted = DocumentService.extract_text_from_file("sample.docx", content)
    assert "Word Intelligence DOCX extraction test." in extracted


def test_document_service_unsupported_format():
    with pytest.raises(DocumentExtractionError) as exc_info:
        DocumentService.extract_text_from_file("script.py", b"print('hello')")
    assert "Unsupported file format" in str(exc_info.value)


def test_document_service_empty_file():
    with pytest.raises(DocumentExtractionError) as exc_info:
        DocumentService.extract_text_from_file("empty.txt", b"")
    assert "empty" in str(exc_info.value)


def test_api_upload_txt_file(client: TestClient):
    file_content = b"Data analytics pipeline with natural language processing."
    files = {"file": ("data.txt", file_content, "text/plain")}
    response = client.post("/api/v1/analysis/file", files=files, data={"top_n": 5})

    assert response.status_code == 200
    data = response.json()
    assert data["total_tokens"] > 0
    assert data["metadata"]["source_type"] == "file"
    assert data["metadata"]["source_name"] == "data.txt"


def test_api_upload_docx_file(client: TestClient):
    docx_bytes = create_in_memory_docx("Scalable document intelligence processing.")
    files = {"file": ("report.docx", docx_bytes, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
    response = client.post("/api/v1/analysis/file", files=files)

    assert response.status_code == 200
    data = response.json()
    assert data["total_tokens"] == 4
    assert data["metadata"]["source_name"] == "report.docx"


def test_api_upload_unsupported_extension(client: TestClient):
    files = {"file": ("payload.exe", b"binarycontent", "application/octet-stream")}
    response = client.post("/api/v1/analysis/file", files=files)
    assert response.status_code == 422
    assert "Unsupported file format" in response.json()["detail"]
