"""Robustness and error handling tests for SceneSpeak.

Corresponds to Section 11.3 and Section 15.1 (T7: Error Paths) of the PDR:
- Bad payload / oversized image (> 2 MB) -> HTTP 413 with speakable error.
- Corrupted image base64 -> graceful fallback with speakable error.
- Schema validation for unknown mode.
- Sanitization and length caps.
- No silent failures: all error paths provide speakable guidance.
"""

import base64
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_oversized_image_rejection():
    """Verify images exceeding 2 MB are rejected with HTTP 413 and a spoken message."""
    # Create a dummy payload larger than 2 MB (2_100_000 bytes)
    oversized_data = b"X" * 2_200_000
    oversized_b64 = base64.b64encode(oversized_data).decode("utf-8")

    payload = {
        "image_b64": oversized_b64,
        "mode": "describe",
    }
    response = client.post("/api/describe", json=payload)
    assert response.status_code == 413
    data = response.json()
    assert "detail" in data
    assert "spoken" in data["detail"]
    assert "too large" in data["detail"]["spoken"]


def test_invalid_mode_validation():
    """Verify unknown operating modes are rejected with Pydantic 422 error."""
    dummy_b64 = base64.b64encode(b"dummy_image_data").decode("utf-8")
    payload = {
        "image_b64": dummy_b64,
        "mode": "fly_airplane",  # invalid mode
    }
    response = client.post("/api/describe", json=payload)
    assert response.status_code == 422


def test_question_length_validation():
    """Verify questions exceeding 200 characters are caught by schema validation."""
    dummy_b64 = base64.b64encode(b"dummy_image_data").decode("utf-8")
    payload = {
        "image_b64": dummy_b64,
        "mode": "ask",
        "question": "A" * 250,  # exceeds max_length 200
    }
    response = client.post("/api/describe", json=payload)
    assert response.status_code == 422


def test_corrupted_base64_recovery():
    """Verify corrupted base64 data produces a speakable error response without server crash."""
    payload = {
        "image_b64": "!!!NOT_VALID_BASE64_###???",
        "mode": "describe",
    }
    response = client.post("/api/describe", json=payload)
    # The endpoint catches the base64 decode exception and returns 500 with spoken fallback
    assert response.status_code == 500
    data = response.json()
    assert "spoken" in data
    assert "trouble" in data["spoken"].lower() or "try again" in data["spoken"].lower()


def test_health_uptime():
    """Verify health check endpoint returns 200."""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
