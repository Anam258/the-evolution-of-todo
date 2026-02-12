"""
Security middleware for the backend application.
Adds security headers to API responses.
"""

from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to all responses.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Add security headers to the response.

        Args:
            request: FastAPI request object
            call_next: Next middleware in the chain

        Returns:
            Response with security headers added
        """
        response: Response = await call_next(request)

        # Set security headers
        # Prevent MIME-type sniffing
        response.headers.setdefault("X-Content-Type-Options", "nosniff")

        # Prevent clickjacking
        response.headers.setdefault("X-Frame-Options", "DENY")

        # Enable XSS protection in older browsers
        response.headers.setdefault("X-XSS-Protection", "1; mode=block")

        # Restrict referrer information
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")

        # Enable HSTS (HTTP Strict Transport Security)
        response.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains; preload")

        # Prevent DNS prefetching
        response.headers.setdefault("X-DNS-Prefetch-Control", "off")

        # Disable external resource loading in IE
        response.headers.setdefault("X-Download-Options", "noopen")

        # Prevent caching of sensitive data
        if "auth" in request.url.path or "login" in request.url.path or "register" in request.url.path:
            # For authentication endpoints, prevent caching
            response.headers.setdefault("Cache-Control", "no-store, no-cache, must-revalidate")
            response.headers.setdefault("Pragma", "no-cache")
            response.headers.setdefault("Expires", "0")

        return response


class CustomCORSMiddleware:
    """
    Custom CORS middleware with additional security headers.
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                # Add security headers to CORS preflight responses
                headers = message.get("headers", [])

                # Add security headers
                security_headers = [
                    (b"x-content-type-options", b"nosniff"),
                    (b"x-frame-options", b"DENY"),
                    (b"x-xss-protection", b"1; mode=block"),
                    (b"referrer-policy", b"strict-origin-when-cross-origin"),
                ]

                # Only add headers that aren't already present
                existing_header_names = {header[0].lower() for header in headers}
                for header_name, header_value in security_headers:
                    if header_name not in existing_header_names:
                        headers.append((header_name, header_value))

                message["headers"] = headers

            await send(message)

        await self.app(scope, receive, send_wrapper)