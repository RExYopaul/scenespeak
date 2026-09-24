"""Unit and integration tests for SceneSpeak API endpoints.

Corresponds to Section 15.4 of the SceneSpeak PDR.
"""

import base64
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_health_check():
    """Verify /api/health returns status 200 and ok."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data


def test_describe_endpoint_with_mock(monkeypatch):
    """Verify /api/describe accepts a valid payload and returns proper schema (PDR T6)."""
    from backend.app import main

    async def mock_gen(*args, **kwargs):
        return (
            "A table is directly ahead, about two steps away. The floor is clear.",
            "mock/test-vlm",
        )

    monkeypatch.setattr(main, "generate_scene_description", mock_gen)

    dummy_b64 = base64.b64encode(b"fake_image_bytes_for_testing").decode("utf-8")
    payload = {
        "image_b64": dummy_b64,
        "mode": "describe",
    }
    response = client.post("/api/describe", json=payload)
    assert response.status_code == 200
    data = response.json()

    # Check contract fields from Section 9.1
    assert "request_id" in data
    assert data["mode"] == "describe"
    assert isinstance(data["text"], str)
    assert isinstance(data["hazard"], bool)
    assert isinstance(data["retake"], bool)
    assert isinstance(data["latency_ms"], int)
    assert "model" in data


def test_feedback_and_stats():
    """Verify submitting feedback and checking stats endpoint."""
    feedback_payload = {
        "request_id": "test_req_01",
        "rating": 5,
        "note": "Clear and fast description",
    }
    fb_res = client.post("/api/feedback", json=feedback_payload)
    assert fb_res.status_code == 200
    assert fb_res.json()["ok"] is True

    stats_res = client.get("/api/stats")
    assert stats_res.status_code == 200
    stats = stats_res.json()
    assert "total_requests" in stats
    assert "avg_latency_ms" in stats
