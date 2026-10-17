import logging
import re
import time
from collections import defaultdict
from typing import Dict, List, Tuple
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from app.core.config import settings

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Applies security-hardening HTTP headers to all incoming API responses,
    mitigating MIME-sniffing, framing/clickjacking, XSS, and unapproved sensor access.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        response: Response = await call_next(request)

        # Defense-in-depth security response headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), camera=(), microphone=()"

        # Content-Security-Policy (CSP)
        if "Content-Security-Policy" not in response.headers:
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
                "font-src 'self' https://fonts.gstatic.com data:; "
                "img-src 'self' data: blob:; "
                "connect-src 'self' http://localhost:* http://127.0.0.1:* ws://localhost:* ws://127.0.0.1:*;"
            )

        return response


class RateLimiter:
    """
    Thread-safe in-memory sliding-window rate limiter per client IP address.
    Prevents abuse and high-frequency flood attacks on resource-intensive endpoints.
    """

    def __init__(self, requests_per_minute: int = 120):
        self.requests_per_minute = requests_per_minute
        self.window_seconds = 60
        self._history: Dict[str, List[float]] = defaultdict(list)

    def is_allowed(self, client_ip: str) -> Tuple[bool, int]:
        """
        Evaluates whether a request from client_ip is within the allowed rate limit.
        Returns (is_allowed, retry_after_seconds).
        """
        now = time.time()
        window_start = now - self.window_seconds
        timestamps = self._history[client_ip]

        # Prune expired timestamps
        valid_timestamps = [t for t in timestamps if t > window_start]
        self._history[client_ip] = valid_timestamps

        if len(valid_timestamps) >= self.requests_per_minute:
            oldest = valid_timestamps[0]
            retry_after = max(1, int(oldest + self.window_seconds - now))
            return False, retry_after

        self._history[client_ip].append(now)
        return True, 0

    def reset(self):
        """Clears all tracking history (used primarily for test isolation)."""
        self._history.clear()


rate_limiter = RateLimiter(requests_per_minute=getattr(settings, "RATE_LIMIT_REQUESTS_PER_MINUTE", 120))


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware applying rate limiting to compute-intensive ingestion and export endpoints.
    Excludes health and readiness probes from throttling.
    """

    PROTECTED_PREFIXES = ("/api/v1/analysis", "/api/v1/export")

    async def dispatch(self, request: Request, call_next) -> Response:
        if not getattr(settings, "RATE_LIMIT_ENABLED", True):
            return await call_next(request)

        path = request.url.path
        if any(path.startswith(prefix) for prefix in self.PROTECTED_PREFIXES):
            # Extract client IP safely
            client_ip = request.client.host if request.client else "127.0.0.1"
            forwarded = request.headers.get("X-Forwarded-For")
            if forwarded:
                client_ip = forwarded.split(",")[0].strip()

            allowed, retry_after = rate_limiter.is_allowed(client_ip)
            if not allowed:
                logger.warning("Rate limit exceeded for client %s on %s", client_ip, path)
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Too many requests. Please slow down and try again later."},
                    headers={"Retry-After": str(retry_after)},
                )

        return await call_next(request)


def sanitize_filename(filename: str) -> str:
    """
    Sanitizes untrusted filenames to prevent directory traversal and null-byte injection.
    Strips directory separators, null characters, and non-printable control codes.
    """
    if not filename:
        return "unnamed_document"

    # Remove null bytes
    cleaned = filename.replace("\0", "")

    # Extract base filename (removes path traversal ../ or ..\)
    cleaned = re.sub(r"[/\\]+", "/", cleaned)
    cleaned = cleaned.split("/")[-1]

    # Remove dangerous characters
    cleaned = re.sub(r'[\x00-\x1f\x7f<>:"|?*]', "", cleaned)

    # Prevent hidden files or leading dots
    cleaned = cleaned.lstrip(".")

    # Enforce safe length boundary
    if len(cleaned) > 200:
        parts = cleaned.rsplit(".", 1)
        if len(parts) == 2:
            cleaned = f"{parts[0][:190]}.{parts[1]}"
        else:
            cleaned = cleaned[:200]

    return cleaned or "document"
