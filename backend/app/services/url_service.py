import ipaddress
import socket
from urllib.parse import urlparse

from bs4 import BeautifulSoup
import httpx

from app.core.config import settings


class URLExtractionError(Exception):
    """Custom exception raised when URL fetching or validation fails."""
    pass


class URLService:
    """
    Secure webpage URL fetching and text extraction service.
    Enforces SSRF protections, DNS resolution validation, redirect tracking,
    response size limits, and clean DOM text parsing.
    """

    MAX_RESPONSE_BYTES = 5 * 1024 * 1024  # 5 MB
    MAX_REDIRECTS = 5

    @classmethod
    def is_ip_allowed(cls, ip_str: str) -> bool:
        """
        Validates that an IP address is publicly routable and not in private,
        loopback, link-local, multicast, or reserved ranges.
        Handles IPv4-mapped IPv6 addresses.
        """
        try:
            ip = ipaddress.ip_address(ip_str)

            # Check if IPv6 maps to an underlying IPv4 address
            if hasattr(ip, "ipv4_mapped") and ip.ipv4_mapped:
                return cls.is_ip_allowed(str(ip.ipv4_mapped))

            # Disallow private, loopback, link-local, multicast, and reserved addresses
            if (
                ip.is_private
                or ip.is_loopback
                or ip.is_link_local
                or ip.is_multicast
                or ip.is_reserved
                or ip.is_unspecified
            ):
                return False
            return True
        except ValueError:
            return False

    @classmethod
    def validate_url_destination(cls, target_url: str) -> str:
        """
        Parses URL and verifies hostname resolves only to permitted public IPs.
        Returns the validated hostname.
        """
        parsed = urlparse(target_url)
        if parsed.scheme.lower() not in ("http", "https"):
            raise URLExtractionError("Only HTTP and HTTPS URLs are permitted.")

        hostname = parsed.hostname
        if not hostname:
            raise URLExtractionError("Invalid URL: missing hostname.")

        # Disallow plain localhost strings directly
        if hostname.lower() in ("localhost", "127.0.0.1", "::1", "0.0.0.0"):
            raise URLExtractionError("Access to localhost or internal network destinations is forbidden.")

        # Check for obfuscated integer or hex IP hostnames
        try:
            if hostname.isdigit():
                direct_ip = ipaddress.ip_address(int(hostname))
                if not cls.is_ip_allowed(str(direct_ip)):
                    raise URLExtractionError(f"Destination '{hostname}' resolves to forbidden IP address '{direct_ip}'.")
            elif hostname.startswith("0x") or hostname.startswith("0X"):
                direct_ip = ipaddress.ip_address(int(hostname, 16))
                if not cls.is_ip_allowed(str(direct_ip)):
                    raise URLExtractionError(f"Destination '{hostname}' resolves to forbidden IP address '{direct_ip}'.")
        except (ValueError, OverflowError):
            pass

        # DNS Resolution & IP Check
        try:
            port = parsed.port or (443 if parsed.scheme.lower() == "https" else 80)
            addr_info = socket.getaddrinfo(hostname, port, type=socket.SOCK_STREAM)
            if not addr_info:
                raise URLExtractionError(f"Could not resolve host '{hostname}'.")

            for family, socktype, proto, canonname, sockaddr in addr_info:
                ip_addr = sockaddr[0]
                if not cls.is_ip_allowed(ip_addr):
                    raise URLExtractionError(
                        f"Destination '{hostname}' resolves to restricted internal IP address '{ip_addr}'."
                    )
        except socket.gaierror:
            raise URLExtractionError(f"DNS lookup failed for hostname '{hostname}'.")
        except URLExtractionError:
            raise
        except Exception as e:
            raise URLExtractionError(f"URL destination validation failed: {str(e)}")

        return hostname

    @classmethod
    def fetch_webpage_text(cls, url: str) -> str:
        """
        Safely retrieves webpage content with SSRF validation across redirects,
        enforces size and time limits, and extracts readable text from HTML.
        """
        current_url = url
        redirect_count = 0

        with httpx.Client(
            timeout=settings.HTTP_REQUEST_TIMEOUT_SECONDS,
            follow_redirects=False,
            headers={"User-Agent": "WordIntelligence/0.4 TextAnalyzer Bot"},
        ) as client:
            while redirect_count <= cls.MAX_REDIRECTS:
                # SSRF validation before every hop
                cls.validate_url_destination(current_url)

                try:
                    response = client.get(current_url)
                except httpx.TimeoutException:
                    raise URLExtractionError("Connection timed out while fetching webpage.")
                except httpx.RequestError as e:
                    raise URLExtractionError(f"Network error while connecting to URL: {str(e)}")

                # Check for redirects
                if response.is_redirect:
                    redirect_count += 1
                    if redirect_count > cls.MAX_REDIRECTS:
                        raise URLExtractionError("Too many redirects encountered.")
                    location = response.headers.get("location")
                    if not location:
                        raise URLExtractionError("Redirect header missing location.")
                    # Resolve relative redirect URLs
                    current_url = str(response.url.join(location))
                    continue

                if response.status_code != 200:
                    raise URLExtractionError(
                        f"Webpage returned non-200 status code: {response.status_code} ({response.reason_phrase})."
                    )

                # Validate content length and type
                content_type = response.headers.get("content-type", "").lower()
                if "text/html" not in content_type and "text/plain" not in content_type:
                    raise URLExtractionError(
                        f"Unsupported webpage Content-Type: '{content_type}'. Expected text/html or text/plain."
                    )

                content_bytes = response.content
                if len(content_bytes) > cls.MAX_RESPONSE_BYTES:
                    raise URLExtractionError("Webpage response size exceeds maximum allowed limit (5 MB).")

                # If plain text, decode and return directly
                if "text/plain" in content_type:
                    return response.text.strip()

                # Parse HTML with BeautifulSoup
                return cls.extract_text_from_html(response.text)

            raise URLExtractionError("Exceeded maximum redirect limit.")

    @classmethod
    def extract_text_from_html(cls, html_content: str) -> str:
        """
        Strips non-content elements (scripts, styles, headers, footers, nav)
        and extracts readable article/body text.
        """
        if not html_content or not html_content.strip():
            raise URLExtractionError("Webpage content is empty.")

        soup = BeautifulSoup(html_content, "html.parser")

        # Strip unneeded structural & executable tags
        for tag in soup(["script", "style", "noscript", "svg", "header", "footer", "nav"]):
            tag.decompose()

        # Extract text with space separation
        text = soup.get_text(separator=" ", strip=True)
        if not text:
            raise URLExtractionError("No readable text could be extracted from the webpage HTML.")

        return text


url_service = URLService()
