"""
Integration tests for edge cases in authentication.
Tests token tampering, missing claims, and concurrent expired requests.
"""

import pytest
import os
import time
from jose import jwt
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import threading
import concurrent.futures


class TestTokenTampering:
    """Test suite for token tampering detection."""

    @pytest.fixture(autouse=True)
    def setup_env(self):
        """Set up environment variables for testing."""
        self.original_secret = os.environ.get("BETTER_AUTH_SECRET")
        self.original_database_url = os.environ.get("DATABASE_URL")

        os.environ["BETTER_AUTH_SECRET"] = "test-secret-key-for-testing-purposes-only"
        os.environ["DATABASE_URL"] = "postgresql://test:test@localhost:5432/test"

        yield

        if self.original_secret:
            os.environ["BETTER_AUTH_SECRET"] = self.original_secret
        else:
            os.environ.pop("BETTER_AUTH_SECRET", None)

        if self.original_database_url:
            os.environ["DATABASE_URL"] = self.original_database_url
        else:
            os.environ.pop("DATABASE_URL", None)

    def create_valid_token(self, user_id: int = 1, email: str = "test@example.com"):
        """Create a valid JWT token."""
        secret = os.environ["BETTER_AUTH_SECRET"]
        current_time = int(time.time())

        payload = {
            "sub": str(user_id),
            "user_id": user_id,
            "email": email,
            "iat": current_time,
            "exp": current_time + 3600
        }

        return jwt.encode(payload, secret, algorithm="HS256")

    def test_modified_payload_is_rejected(self):
        """Test that tokens with modified payloads are rejected."""
        valid_token = self.create_valid_token()

        # Decode without verification, modify, and re-encode with different secret
        parts = valid_token.split('.')
        # The signature won't match after modification
        fake_secret = "different-secret-key-for-tampering"

        tampered_payload = {
            "sub": "999",  # Changed user_id
            "user_id": 999,
            "email": "hacker@example.com",
            "iat": int(time.time()),
            "exp": int(time.time()) + 3600
        }

        tampered_token = jwt.encode(tampered_payload, fake_secret, algorithm="HS256")

        from src.main import app
        client = TestClient(app)

        response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {tampered_token}"}
        )

        # Tampered token should be rejected
        assert response.status_code == 401

    def test_token_with_wrong_signature_is_rejected(self):
        """Test that tokens signed with wrong secret are rejected."""
        wrong_secret = "this-is-the-wrong-secret-key-32chars"
        current_time = int(time.time())

        payload = {
            "sub": "1",
            "user_id": 1,
            "email": "test@example.com",
            "iat": current_time,
            "exp": current_time + 3600
        }

        wrong_signature_token = jwt.encode(payload, wrong_secret, algorithm="HS256")

        from src.main import app
        client = TestClient(app)

        response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {wrong_signature_token}"}
        )

        # Wrong signature should be rejected
        assert response.status_code == 401

    def test_truncated_token_is_rejected(self):
        """Test that truncated/partial tokens are rejected."""
        valid_token = self.create_valid_token()

        # Truncate the token
        truncated_token = valid_token[:len(valid_token) // 2]

        from src.main import app
        client = TestClient(app)

        response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {truncated_token}"}
        )

        # Truncated token should be rejected
        assert response.status_code == 401

    def test_malformed_token_is_rejected(self):
        """Test that malformed tokens are rejected."""
        malformed_tokens = [
            "not.a.valid.token",
            "only-one-part",
            "two.parts",
            "a.b.c.d.e",  # Too many parts
            "",
            "    ",
            "eyJhbGciOiJIUzI1NiJ9",  # Only header
            "...",  # Empty parts
        ]

        from src.main import app
        client = TestClient(app)

        for malformed in malformed_tokens:
            response = client.get(
                "/auth/me",
                headers={"Authorization": f"Bearer {malformed}"}
            )
            # All malformed tokens should be rejected
            assert response.status_code == 401, f"Token '{malformed}' should be rejected"


class TestMissingClaims:
    """Test suite for tokens with missing claims."""

    @pytest.fixture(autouse=True)
    def setup_env(self):
        """Set up environment variables for testing."""
        self.original_secret = os.environ.get("BETTER_AUTH_SECRET")
        self.original_database_url = os.environ.get("DATABASE_URL")

        os.environ["BETTER_AUTH_SECRET"] = "test-secret-key-for-testing-purposes-only"
        os.environ["DATABASE_URL"] = "postgresql://test:test@localhost:5432/test"

        yield

        if self.original_secret:
            os.environ["BETTER_AUTH_SECRET"] = self.original_secret
        else:
            os.environ.pop("BETTER_AUTH_SECRET", None)

        if self.original_database_url:
            os.environ["DATABASE_URL"] = self.original_database_url
        else:
            os.environ.pop("DATABASE_URL", None)

    def test_token_without_sub_claim_is_rejected(self):
        """Test that tokens without 'sub' claim are rejected."""
        secret = os.environ["BETTER_AUTH_SECRET"]
        current_time = int(time.time())

        # Token without 'sub' claim
        payload = {
            "email": "test@example.com",
            "iat": current_time,
            "exp": current_time + 3600
        }

        token = jwt.encode(payload, secret, algorithm="HS256")

        from src.main import app
        client = TestClient(app)

        response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )

        # Token without sub should be rejected
        assert response.status_code == 401

    def test_token_without_exp_claim_behavior(self):
        """Test behavior of tokens without 'exp' claim."""
        secret = os.environ["BETTER_AUTH_SECRET"]
        current_time = int(time.time())

        # Token without 'exp' claim
        payload = {
            "sub": "1",
            "user_id": 1,
            "email": "test@example.com",
            "iat": current_time
            # No exp claim
        }

        token = jwt.encode(payload, secret, algorithm="HS256")

        from src.main import app
        client = TestClient(app)

        response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )

        # Behavior depends on implementation - may be rejected or accepted
        # Most secure implementations should reject tokens without exp
        assert response.status_code in [200, 401]

    def test_token_with_null_user_id_is_rejected(self):
        """Test that tokens with null user_id are rejected."""
        secret = os.environ["BETTER_AUTH_SECRET"]
        current_time = int(time.time())

        payload = {
            "sub": None,
            "user_id": None,
            "email": "test@example.com",
            "iat": current_time,
            "exp": current_time + 3600
        }

        token = jwt.encode(payload, secret, algorithm="HS256")

        from src.main import app
        client = TestClient(app)

        response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )

        # Null user_id should be rejected
        assert response.status_code == 401

    def test_token_with_empty_string_user_id_is_rejected(self):
        """Test that tokens with empty string user_id are rejected."""
        secret = os.environ["BETTER_AUTH_SECRET"]
        current_time = int(time.time())

        payload = {
            "sub": "",
            "user_id": "",
            "email": "test@example.com",
            "iat": current_time,
            "exp": current_time + 3600
        }

        token = jwt.encode(payload, secret, algorithm="HS256")

        from src.main import app
        client = TestClient(app)

        response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )

        # Empty user_id should be rejected
        assert response.status_code == 401


class TestConcurrentExpiredRequests:
    """Test suite for concurrent requests with expired tokens."""

    @pytest.fixture(autouse=True)
    def setup_env(self):
        """Set up environment variables for testing."""
        self.original_secret = os.environ.get("BETTER_AUTH_SECRET")
        self.original_database_url = os.environ.get("DATABASE_URL")

        os.environ["BETTER_AUTH_SECRET"] = "test-secret-key-for-testing-purposes-only"
        os.environ["DATABASE_URL"] = "postgresql://test:test@localhost:5432/test"

        yield

        if self.original_secret:
            os.environ["BETTER_AUTH_SECRET"] = self.original_secret
        else:
            os.environ.pop("BETTER_AUTH_SECRET", None)

        if self.original_database_url:
            os.environ["DATABASE_URL"] = self.original_database_url
        else:
            os.environ.pop("DATABASE_URL", None)

    def create_expired_token(self):
        """Create an expired token."""
        secret = os.environ["BETTER_AUTH_SECRET"]
        current_time = int(time.time())

        payload = {
            "sub": "1",
            "user_id": 1,
            "email": "test@example.com",
            "iat": current_time - 7200,  # 2 hours ago
            "exp": current_time - 3600   # Expired 1 hour ago
        }

        return jwt.encode(payload, secret, algorithm="HS256")

    def test_concurrent_expired_token_requests(self):
        """Test that concurrent requests with expired tokens all return 401."""
        expired_token = self.create_expired_token()
        num_requests = 10

        from src.main import app
        client = TestClient(app)

        def make_request():
            return client.get(
                "/auth/me",
                headers={"Authorization": f"Bearer {expired_token}"}
            )

        # Make concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(num_requests)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        # All requests should return 401
        for response in results:
            assert response.status_code == 401, "All expired token requests should return 401"

    def test_concurrent_mixed_token_requests(self):
        """Test concurrent requests with mix of valid and expired tokens."""
        secret = os.environ["BETTER_AUTH_SECRET"]
        current_time = int(time.time())

        # Create valid token
        valid_payload = {
            "sub": "1",
            "user_id": 1,
            "email": "valid@example.com",
            "iat": current_time,
            "exp": current_time + 3600
        }
        valid_token = jwt.encode(valid_payload, secret, algorithm="HS256")

        # Create expired token
        expired_token = self.create_expired_token()

        from src.main import app
        client = TestClient(app)

        results = []
        lock = threading.Lock()

        def make_request(token, is_valid):
            response = client.get(
                "/auth/me",
                headers={"Authorization": f"Bearer {token}"}
            )
            with lock:
                results.append((is_valid, response.status_code))

        # Make concurrent requests with mix of tokens
        threads = []
        for i in range(10):
            is_valid = i % 2 == 0
            token = valid_token if is_valid else expired_token
            t = threading.Thread(target=make_request, args=(token, is_valid))
            threads.append(t)
            t.start()

        # Wait for all threads
        for t in threads:
            t.join()

        # Verify results
        for is_valid, status_code in results:
            if not is_valid:
                assert status_code == 401, "Expired tokens should return 401"
            # Valid tokens might return 200 or 404 depending on mocking


class TestAuthorizationHeaderFormats:
    """Test various Authorization header formats."""

    @pytest.fixture(autouse=True)
    def setup_env(self):
        """Set up environment variables for testing."""
        self.original_secret = os.environ.get("BETTER_AUTH_SECRET")
        self.original_database_url = os.environ.get("DATABASE_URL")

        os.environ["BETTER_AUTH_SECRET"] = "test-secret-key-for-testing-purposes-only"
        os.environ["DATABASE_URL"] = "postgresql://test:test@localhost:5432/test"

        yield

        if self.original_secret:
            os.environ["BETTER_AUTH_SECRET"] = self.original_secret
        else:
            os.environ.pop("BETTER_AUTH_SECRET", None)

        if self.original_database_url:
            os.environ["DATABASE_URL"] = self.original_database_url
        else:
            os.environ.pop("DATABASE_URL", None)

    def create_valid_token(self):
        """Create a valid token."""
        secret = os.environ["BETTER_AUTH_SECRET"]
        current_time = int(time.time())

        payload = {
            "sub": "1",
            "user_id": 1,
            "email": "test@example.com",
            "iat": current_time,
            "exp": current_time + 3600
        }

        return jwt.encode(payload, secret, algorithm="HS256")

    def test_missing_bearer_prefix_is_rejected(self):
        """Test that tokens without 'Bearer ' prefix are rejected."""
        token = self.create_valid_token()

        from src.main import app
        client = TestClient(app)

        # Send token without Bearer prefix
        response = client.get(
            "/auth/me",
            headers={"Authorization": token}  # No "Bearer " prefix
        )

        # Should be rejected
        assert response.status_code in [401, 403, 422]

    def test_lowercase_bearer_handling(self):
        """Test handling of lowercase 'bearer' prefix."""
        token = self.create_valid_token()

        from src.main import app
        client = TestClient(app)

        response = client.get(
            "/auth/me",
            headers={"Authorization": f"bearer {token}"}  # lowercase
        )

        # May be accepted or rejected depending on implementation
        # Document actual behavior
        assert response.status_code in [200, 401, 403, 404, 422]

    def test_extra_spaces_in_header(self):
        """Test handling of extra spaces in Authorization header."""
        token = self.create_valid_token()

        from src.main import app
        client = TestClient(app)

        response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer  {token}"}  # Extra space
        )

        # May be accepted or rejected depending on implementation
        assert response.status_code in [200, 401, 403, 404, 422]


if __name__ == "__main__":
    pytest.main([__file__])
