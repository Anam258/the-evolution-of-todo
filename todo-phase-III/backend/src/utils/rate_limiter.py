"""
Rate limiting utilities for the backend application.
Provides rate limiting functionality for authentication endpoints.
"""

import time
from collections import defaultdict, deque
from typing import Dict, Optional
from threading import Lock
import hashlib


class RateLimiter:
    """
    A simple in-memory rate limiter using sliding window algorithm.
    """

    def __init__(self):
        # Dictionary to store rate limit data for each key
        # Format: {key: deque of timestamps}
        self.requests = defaultdict(deque)
        # Thread lock for thread-safe operations
        self.lock = Lock()

    def is_allowed(self, key: str, max_requests: int, window_size: int) -> bool:
        """
        Check if a request is allowed based on rate limits.

        Args:
            key: Unique identifier for the client (e.g., IP address, user ID)
            max_requests: Maximum number of requests allowed in the window
            window_size: Time window in seconds

        Returns:
            True if request is allowed, False otherwise
        """
        with self.lock:
            current_time = time.time()
            window_start = current_time - window_size

            # Remove outdated requests
            while self.requests[key] and self.requests[key][0] < window_start:
                self.requests[key].popleft()

            # Check if we're under the limit
            if len(self.requests[key]) < max_requests:
                # Add current request
                self.requests[key].append(current_time)
                return True

            # Rate limit exceeded
            return False

    def get_reset_time(self, key: str, window_size: int) -> float:
        """
        Get the time when the rate limit window resets for a key.

        Args:
            key: Unique identifier for the client
            window_size: Time window in seconds

        Returns:
            Unix timestamp when the rate limit window resets
        """
        with self.lock:
            if not self.requests[key]:
                return time.time()

            # Reset time is the oldest request time + window size
            oldest_request = self.requests[key][0]
            return oldest_request + window_size


# Global rate limiter instance
rate_limiter = RateLimiter()


class AuthRateLimiter:
    """
    Rate limiter specifically for authentication endpoints.
    """

    def __init__(self):
        self.login_attempts_limiter = RateLimiter()
        self.registration_limiter = RateLimiter()

        # Rate limit settings
        self.LOGIN_ATTEMPTS_LIMIT = 5  # per 15 minutes
        self.LOGIN_WINDOW_SIZE = 900  # 15 minutes in seconds
        self.REGISTRATION_LIMIT = 2  # per hour
        self.REGISTRATION_WINDOW_SIZE = 3600  # 1 hour in seconds
        self.PASSWORD_RESET_LIMIT = 3  # per hour
        self.PASSWORD_RESET_WINDOW_SIZE = 3600  # 1 hour in seconds

    def is_login_allowed(self, identifier: str) -> tuple[bool, Optional[float]]:
        """
        Check if a login attempt is allowed for the given identifier.

        Args:
            identifier: Unique identifier (e.g., IP address, email)

        Returns:
            Tuple of (is_allowed, reset_time_if_limited)
        """
        is_allowed = self.login_attempts_limiter.is_allowed(
            identifier,
            self.LOGIN_ATTEMPTS_LIMIT,
            self.LOGIN_WINDOW_SIZE
        )

        if not is_allowed:
            reset_time = self.login_attempts_limiter.get_reset_time(
                identifier,
                self.LOGIN_WINDOW_SIZE
            )
            return False, reset_time

        return True, None

    def is_registration_allowed(self, identifier: str) -> tuple[bool, Optional[float]]:
        """
        Check if a registration attempt is allowed for the given identifier.

        Args:
            identifier: Unique identifier (e.g., IP address, email)

        Returns:
            Tuple of (is_allowed, reset_time_if_limited)
        """
        is_allowed = self.registration_limiter.is_allowed(
            identifier,
            self.REGISTRATION_LIMIT,
            self.REGISTRATION_WINDOW_SIZE
        )

        if not is_allowed:
            reset_time = self.registration_limiter.get_reset_time(
                identifier,
                self.REGISTRATION_WINDOW_SIZE
            )
            return False, reset_time

        return True, None

    def is_password_reset_allowed(self, identifier: str) -> tuple[bool, Optional[float]]:
        """
        Check if a password reset attempt is allowed for the given identifier.

        Args:
            identifier: Unique identifier (e.g., IP address, email)

        Returns:
            Tuple of (is_allowed, reset_time_if_limited)
        """
        is_allowed = rate_limiter.is_allowed(
            identifier,
            self.PASSWORD_RESET_LIMIT,
            self.PASSWORD_RESET_WINDOW_SIZE
        )

        if not is_allowed:
            reset_time = rate_limiter.get_reset_time(
                identifier,
                self.PASSWORD_RESET_WINDOW_SIZE
            )
            return False, reset_time

        return True, None

    def get_rate_limit_headers(self, is_allowed: bool, reset_time: Optional[float] = None) -> Dict[str, str]:
        """
        Get rate limit headers to include in the response.

        Args:
            is_allowed: Whether the request is allowed
            reset_time: Time when the rate limit resets

        Returns:
            Dictionary of headers to include in the response
        """
        headers = {}

        if reset_time:
            headers['X-RateLimit-Reset'] = str(int(reset_time))
            headers['Retry-After'] = str(int(reset_time - time.time()))

        return headers


# Global auth rate limiter instance
auth_rate_limiter = AuthRateLimiter()


def get_client_ip(request) -> str:
    """
    Extract client IP address from the request.

    Args:
        request: FastAPI request object

    Returns:
        Client IP address
    """
    # Check for forwarded IP header (common in proxy setups)
    forwarded_for = request.headers.get('X-Forwarded-For')
    if forwarded_for:
        # Take the first IP in case of multiple proxies
        return forwarded_for.split(',')[0].strip()

    # Check for other common headers
    real_ip = request.headers.get('X-Real-IP')
    if real_ip:
        return real_ip

    # Fallback to client host
    if request.client and request.client.host:
        return request.client.host

    # Default fallback
    return "unknown"


def get_rate_limit_key(identifier: str, endpoint: str) -> str:
    """
    Create a rate limit key combining identifier and endpoint.

    Args:
        identifier: Unique identifier (e.g., IP address, user ID)
        endpoint: API endpoint

    Returns:
        Combined rate limit key
    """
    # Hash the combination to avoid special characters in keys
    combined = f"{identifier}:{endpoint}"
    return hashlib.sha256(combined.encode()).hexdigest()[:16]