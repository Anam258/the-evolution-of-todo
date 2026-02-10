"""
Token cleanup utilities for the backend application.
Handles cleanup of expired tokens and maintenance tasks.
"""

import time
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from jose import jwt, JWTError
import os


class TokenCleanupService:
    """
    Service for cleaning up expired tokens and performing maintenance tasks.
    Note: For JWT tokens, which are stateless, actual cleanup is not typically required
    since they are self-contained and expire automatically. However, this service
    provides utilities for token validation and cleanup of any stored token metadata.
    """

    def __init__(self):
        self.secret_key = os.getenv("BETTER_AUTH_SECRET", "your-32-character-secret-key-here")
        self.algorithm = os.getenv("JWT_ALGORITHM", "HS256")

    def is_token_expired(self, token: str) -> bool:
        """
        Check if a JWT token is expired without verifying its signature.

        Args:
            token: JWT token string to check

        Returns:
            True if token is expired, False otherwise
        """
        try:
            # Decode the token without verification to check expiration
            # This is safe for expiration checking only
            payload = jwt.get_unverified_claims(token)

            exp_timestamp = payload.get("exp")
            if not exp_timestamp:
                return True  # Token without expiration is considered expired

            current_timestamp = int(time.time())
            return current_timestamp > exp_timestamp
        except JWTError:
            # If we can't decode the token, consider it invalid/expired
            return True
        except Exception:
            # Any other error means we can't validate the token
            return True

    def filter_expired_tokens(self, tokens: List[str]) -> List[str]:
        """
        Filter out expired tokens from a list.

        Args:
            tokens: List of JWT token strings

        Returns:
            List of valid (non-expired) tokens
        """
        valid_tokens = []
        for token in tokens:
            if not self.is_token_expired(token):
                valid_tokens.append(token)
        return valid_tokens

    def get_token_details(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Get details from a token without verifying its signature.

        Args:
            token: JWT token string

        Returns:
            Token payload if decodable, None otherwise
        """
        try:
            payload = jwt.get_unverified_claims(token)
            return payload
        except Exception:
            return None

    def get_time_until_expiration(self, token: str) -> Optional[int]:
        """
        Get the time in seconds until a token expires.

        Args:
            token: JWT token string

        Returns:
            Seconds until expiration, or None if token is invalid
        """
        details = self.get_token_details(token)
        if not details or 'exp' not in details:
            return None

        exp_timestamp = details['exp']
        current_timestamp = int(time.time())

        if current_timestamp >= exp_timestamp:
            return 0  # Already expired

        return exp_timestamp - current_timestamp

    def cleanup_expired_sessions(self, user_sessions: Dict[str, str]) -> Dict[str, str]:
        """
        Clean up expired sessions from a dictionary of user sessions.

        Args:
            user_sessions: Dictionary mapping user identifiers to their tokens

        Returns:
            Dictionary with only valid (non-expired) sessions
        """
        valid_sessions = {}
        for user_id, token in user_sessions.items():
            if not self.is_token_expired(token):
                valid_sessions[user_id] = token
        return valid_sessions

    def schedule_periodic_cleanup(self, interval_seconds: int = 3600) -> None:
        """
        Schedule periodic cleanup of expired tokens.
        Note: This would typically be run in a background task/celery worker.

        Args:
            interval_seconds: How often to run cleanup in seconds (default: 1 hour)
        """
        print(f"Scheduled token cleanup to run every {interval_seconds} seconds")
        # In a real implementation, this would be scheduled with a task scheduler
        # like Celery, APScheduler, or similar


class BackgroundTokenCleanup:
    """
    Background service to periodically clean up expired tokens.
    """

    def __init__(self):
        self.cleanup_service = TokenCleanupService()

    def run_cleanup_task(self):
        """
        Run the token cleanup task.
        In a real implementation, this would be called by a background scheduler.
        """
        print(f"[{datetime.now()}] Running token cleanup task...")

        # In a real implementation, you would:
        # 1. Query the database for stored tokens/metadata
        # 2. Check which ones are expired
        # 3. Remove the expired entries

        print(f"[{datetime.now()}] Token cleanup task completed.")


# Global instance
token_cleanup_service = TokenCleanupService()
background_cleanup = BackgroundTokenCleanup()


def run_cleanup_job():
    """
    Function to run the cleanup job, suitable for scheduling.
    """
    background_cleanup.run_cleanup_task()


if __name__ == "__main__":
    # Example usage
    example_token = jwt.encode(
        {"sub": "test_user", "exp": int(time.time()) + 3600},  # Expires in 1 hour
        os.getenv("BETTER_AUTH_SECRET", "test-secret"),
        algorithm="HS256"
    )

    print("Example token:", example_token)
    print("Is expired:", token_cleanup_service.is_token_expired(example_token))

    details = token_cleanup_service.get_token_details(example_token)
    print("Token details:", details)

    time_until_exp = token_cleanup_service.get_time_until_expiration(example_token)
    print("Time until expiration (seconds):", time_until_exp)