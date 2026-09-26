"""
Unit and integration tests for Phase 6 Copilot Endpoints connecting to Phase 5.
"""

from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


def test_api_copilot_ask_hinglish():
    payload = {
        "query": "Kal kitni bikri hui thi?",
        "session_id": "test_session_1",
        "merchant_id": "M001",
        "language": "hinglish"
    }
    response = client.post("/api/copilot/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["answer"] != ""
    assert data["intent"] == "SALES_SUMMARY"
    assert data["language"] == "hinglish"
    assert data["validation_status"] == "PASSED"
    assert len(data["sources"]) > 0


def test_api_copilot_ask_hindi():
    payload = {
        "query": "मेरी कुल बिक्री कितनी रही है?",
        "session_id": "test_session_2",
        "merchant_id": "M001",
        "language": "hindi"
    }
    response = client.post("/api/copilot/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "कुल बिक्री" in data["answer"]
    assert data["language"] == "hi"


def test_api_copilot_daily_brief():
    response = client.get("/api/copilot/daily-brief?language=hinglish")
    assert response.status_code == 200
    data = response.json()
    assert "brief" in data
    assert data["brief"]["answer"] != ""
    assert len(data["brief"]["recommendations"]) > 0


def test_api_copilot_ask_benchmark():
    payload = {
        "query": "Meri dukaan dusron se kaisi hai?",
        "session_id": "test_session_bench",
        "merchant_id": "M015",
        "language": "hinglish"
    }
    response = client.post("/api/copilot/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "BENCHMARK"
    assert "rank" in data["answer"].lower() or "score" in data["answer"].lower()
    assert len(data["sources"]) > 0

