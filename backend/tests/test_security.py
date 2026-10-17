import io
import pytest
from starlette.testclient import TestClient
from app.main import app
from app.core.security import rate_limiter, sanitize_filename
from app.services.url_service import URLService, URLExtractionError


@pytest.fixture
def client():
    rate_limiter.reset()
    yield TestClient(app)
    rate_limiter.reset()


def test_security_headers_present_on_responses(client: TestClient):
    """Verify standard security headers are applied to all API responses."""
    response = client.get("/health")
    assert response.status_code == 200

    headers = response.headers
    assert headers.get("X-Content-Type-Options") == "nosniff"
    assert headers.get("X-Frame-Options") == "DENY"
    assert headers.get("X-XSS-Protection") == "1; mode=block"
    assert headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
    assert "geolocation=()" in headers.get("Permissions-Policy", "")
    assert "default-src 'self'" in headers.get("Content-Security-Policy", "")


def test_rate_limiter_blocks_flooding(client: TestClient):
    """Verify rate limiter blocks client IP after threshold and returns 429 with Retry-After."""
    # Temporarily set a low threshold for the test
    original_limit = rate_limiter.requests_per_minute
    rate_limiter.requests_per_minute = 5
    rate_limiter.reset()

    try:
        payload = {"text": "Security rate limit test input.", "top_n": 5}

        # First 5 requests should pass
        for _ in range(5):
            res = client.post("/api/v1/analysis", json=payload)
            assert res.status_code == 200

        # 6th request must trigger HTTP 429
        blocked_res = client.post("/api/v1/analysis", json=payload)
        assert blocked_res.status_code == 429
        assert "Retry-After" in blocked_res.headers
        assert "Too many requests" in blocked_res.json()["detail"]

        # Health endpoint should never be blocked by rate limiter
        health_res = client.get("/health")
        assert health_res.status_code == 200
    finally:
        rate_limiter.requests_per_minute = original_limit
        rate_limiter.reset()


def test_filename_sanitization():
    """Verify sanitize_filename cleans directory traversal, null bytes, and control chars."""
    assert sanitize_filename("../../etc/passwd.txt") == "passwd.txt"
    assert sanitize_filename("..\\..\\windows\\system32\\cmd.exe.docx") == "cmd.exe.docx"
    assert sanitize_filename("safe_report.pdf") == "safe_report.pdf"
    assert sanitize_filename("null\0byte.txt") == "nullbyte.txt"
    assert sanitize_filename(".hidden_file.txt") == "hidden_file.txt"
    assert sanitize_filename("") == "unnamed_document"


def test_upload_path_traversal_safe(client: TestClient):
    """Verify document upload handles path-traversal filename safely."""
    file_content = b"Safe report text content."
    file_tuple = ("../../malicious_traversal.txt", io.BytesIO(file_content), "text/plain")

    response = client.post(
        "/api/v1/analysis/file",
        files={"file": file_tuple},
        data={"top_n": "5"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_tokens"] > 0
    # Source name in metadata should be sanitized
    assert "/" not in data["metadata"]["source_name"]
    assert ".." not in data["metadata"]["source_name"]


def test_ssrf_obfuscated_ips_blocked():
    """Verify SSRF validation blocks decimal, hex, and mapped loopback representations."""
    # Decimal IP 2130706433 = 127.0.0.1
    with pytest.raises(URLExtractionError):
        URLService.validate_url_destination("http://2130706433/admin")

    # Hex IP 0x7f000001 = 127.0.0.1
    with pytest.raises(URLExtractionError):
        URLService.validate_url_destination("http://0x7f000001/admin")

    # IPv4-mapped IPv6 loopback
    assert URLService.is_ip_allowed("::ffff:127.0.0.1") is False

    # Standard loopback and private IPs
    assert URLService.is_ip_allowed("127.0.0.1") is False
    assert URLService.is_ip_allowed("10.0.0.1") is False
    assert URLService.is_ip_allowed("192.168.1.1") is False
    assert URLService.is_ip_allowed("169.254.169.254") is False
    assert URLService.is_ip_allowed("8.8.8.8") is True
