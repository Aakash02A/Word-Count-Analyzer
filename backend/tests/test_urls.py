import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.url_service import URLExtractionError, URLService


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_url_service_ip_filtering():
    """Verify internal and reserved IPs are blocked by the IP validator."""
    assert not URLService.is_ip_allowed("127.0.0.1")
    assert not URLService.is_ip_allowed("10.0.0.1")
    assert not URLService.is_ip_allowed("192.168.1.1")
    assert not URLService.is_ip_allowed("172.16.0.1")
    assert not URLService.is_ip_allowed("169.254.169.254")
    assert not URLService.is_ip_allowed("::1")
    assert not URLService.is_ip_allowed("0.0.0.0")

    # Public IPs should be allowed
    assert URLService.is_ip_allowed("8.8.8.8")
    assert URLService.is_ip_allowed("1.1.1.1")


def test_url_service_rejects_localhost():
    with pytest.raises(URLExtractionError) as exc_info:
        URLService.validate_url_destination("http://localhost:8000/secret")
    assert "forbidden" in str(exc_info.value).lower()


def test_url_service_rejects_non_http_schemes():
    with pytest.raises(URLExtractionError) as exc_info:
        URLService.validate_url_destination("ftp://example.com/file.txt")
    assert "Only HTTP and HTTPS" in str(exc_info.value)


def test_url_service_html_extraction():
    html = """
    <!DOCTYPE html>
    <html>
        <head><title>Test Title</title><style>.hidden { display: none; }</style></head>
        <body>
            <header>Header nav</header>
            <script>console.log("ignore me");</script>
            <article>
                <h1>Article Heading</h1>
                <p>This is readable content extracted cleanly.</p>
            </article>
            <footer>Footer notice</footer>
        </body>
    </html>
    """
    text = URLService.extract_text_from_html(html)
    assert "Article Heading" in text
    assert "This is readable content extracted cleanly." in text
    assert "console.log" not in text
    assert "display: none" not in text
    assert "Footer notice" not in text


def test_api_analyze_url_ssrf_blocked(client: TestClient):
    """Verify API rejects requests targeting localhost or internal infrastructure."""
    response = client.post("/api/v1/analysis/url", json={"url": "http://127.0.0.1:8000/admin"})
    assert response.status_code == 422
    assert "forbidden" in response.json()["detail"].lower()
