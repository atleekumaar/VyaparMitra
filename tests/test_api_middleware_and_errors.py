"""
Unit tests for API middleware, X-Request-ID, and structured error envelopes.
"""

from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


def test_request_id_propagation():
    custom_id = "test-req-custom-12345"
    response = client.get("/api/health", headers={"X-Request-ID": custom_id})
    assert response.status_code == 200
    assert response.headers.get("X-Request-ID") == custom_id


def test_error_envelope_404():
    response = client.get("/api/some_non_existent_route")
    assert response.status_code == 404
    err = response.json()
    assert "error" in err
    assert "code" in err["error"]
    assert "message" in err["error"]
    assert "request_id" in err["error"]


def test_error_envelope_422():
    # Sending invalid data type for limit query parameter
    response = client.get("/api/dashboard/actions?limit=invalid_number")
    assert response.status_code == 422
    err = response.json()
    assert "error" in err
    assert err["error"]["code"] == "VALIDATION_ERROR"
    assert "details" in err["error"]
