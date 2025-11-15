"""
Security Middleware and Headers.
Provides security headers, HTTPS enforcement, and protection mechanisms.
"""
from fastapi import Request, Response
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
import structlog

from app.core.config import settings

logger = structlog.get_logger()


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to all responses.

    Security headers implemented:
    - X-Content-Type-Options: Prevent MIME type sniffing
    - X-Frame-Options: Prevent clickjacking
    - X-XSS-Protection: Enable XSS filter
    - Strict-Transport-Security: Force HTTPS
    - Content-Security-Policy: Prevent XSS attacks
    - Referrer-Policy: Control referrer information
    - Permissions-Policy: Control browser features
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Process request
        response = await call_next(request)

        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Content Security Policy
        csp_directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com https://cdn.jsdelivr.net",
            "style-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com",
            "img-src 'self' data: https:",
            "font-src 'self' data:",
            "connect-src 'self' http://localhost:* ws://localhost:*",
            "frame-ancestors 'none'",
        ]
        response.headers["Content-Security-Policy"] = "; ".join(csp_directives)

        # Permissions Policy (formerly Feature-Policy)
        permissions = [
            "geolocation=()",
            "microphone=()",
            "camera=()",
            "payment=()",
            "usb=()",
        ]
        response.headers["Permissions-Policy"] = ", ".join(permissions)

        # HSTS (HTTP Strict Transport Security) - only in production
        if settings.is_production():
            # max-age=31536000 (1 year), includeSubDomains, preload
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains; preload"
            )

        return response


class HTTPSRedirectMiddleware(BaseHTTPMiddleware):
    """
    Middleware to enforce HTTPS in production environments.
    Redirects all HTTP requests to HTTPS.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Only enforce HTTPS in production
        if not settings.is_production():
            return await call_next(request)

        # Check if request is already HTTPS
        if request.url.scheme == "https":
            return await call_next(request)

        # Check X-Forwarded-Proto header (for reverse proxies)
        forwarded_proto = request.headers.get("X-Forwarded-Proto", "")
        if forwarded_proto == "https":
            return await call_next(request)

        # Redirect to HTTPS
        https_url = request.url.replace(scheme="https")
        logger.info(
            "Redirecting HTTP to HTTPS",
            original_url=str(request.url),
            redirect_url=str(https_url)
        )

        return RedirectResponse(
            url=str(https_url),
            status_code=301  # Permanent redirect
        )


class RateLimitExceeded(Exception):
    """Exception raised when rate limit is exceeded."""
    pass


def get_real_ip(request: Request) -> str:
    """
    Get the real client IP address, accounting for proxies.

    Args:
        request: FastAPI request object

    Returns:
        Client IP address
    """
    # Check X-Forwarded-For header (from reverse proxy)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # Take the first IP (client IP)
        return forwarded_for.split(",")[0].strip()

    # Check X-Real-IP header
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip

    # Fallback to direct client IP
    return request.client.host if request.client else "unknown"


def validate_input_size(content: str, max_size: int = 10000) -> bool:
    """
    Validate input size to prevent DoS attacks.

    Args:
        content: Input content
        max_size: Maximum allowed size in characters

    Returns:
        True if valid, False otherwise
    """
    return len(content) <= max_size


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent path traversal attacks.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename
    """
    # Remove path components
    filename = filename.split("/")[-1].split("\\")[-1]

    # Remove dangerous characters
    dangerous_chars = ["<", ">", ":", '"', "/", "\\", "|", "?", "*", "\0"]
    for char in dangerous_chars:
        filename = filename.replace(char, "_")

    # Limit length
    if len(filename) > 255:
        filename = filename[:255]

    return filename


def is_safe_redirect_url(url: str, allowed_hosts: list) -> bool:
    """
    Check if a redirect URL is safe (prevents open redirect vulnerabilities).

    Args:
        url: URL to validate
        allowed_hosts: List of allowed host names

    Returns:
        True if safe, False otherwise
    """
    if not url:
        return False

    # Relative URLs are safe
    if url.startswith("/"):
        return True

    # Check if URL is in allowed hosts
    from urllib.parse import urlparse
    parsed = urlparse(url)

    if parsed.netloc in allowed_hosts:
        return True

    return False
