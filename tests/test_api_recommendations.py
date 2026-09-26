"""
Unit and integration tests for Phase 6 Recommendation and Action Center Endpoints.
"""

from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


def test_api_list_recommendations():
    response = client.get("/api/recommendations?limit=20")
    assert response.status_code == 200
    data = response.json()
    assert "total_count" in data
    assert "recommendations" in data
    assert len(data["recommendations"]) > 0
    first = data["recommendations"][0]
    assert "recommendation_id" in first
    assert "priority_band" in first
    assert "evidence" in first


def test_api_recommendation_detail_and_status_update():
    list_res = client.get("/api/recommendations?limit=1")
    rec_id = list_res.json()["recommendations"][0]["recommendation_id"]

    # 1. Detail
    detail_res = client.get(f"/api/recommendations/{rec_id}")
    assert detail_res.status_code == 200
    assert detail_res.json()["recommendation_id"] == rec_id

    # 2. Update status to ACCEPTED
    update_res = client.post(
        f"/api/recommendations/{rec_id}/status",
        json={"status": "ACCEPTED"}
    )
    assert update_res.status_code == 200
    up_data = update_res.json()
    assert up_data["new_status"] == "ACCEPTED"
    assert up_data["recommendation_id"] == rec_id

    # 3. Verify detail reflects new status
    check_res = client.get(f"/api/recommendations/{rec_id}")
    assert check_res.json()["status"] == "ACCEPTED"


def test_api_recommendation_invalid_status():
    list_res = client.get("/api/recommendations?limit=1")
    rec_id = list_res.json()["recommendations"][0]["recommendation_id"]

    bad_res = client.post(
        f"/api/recommendations/{rec_id}/status",
        json={"status": "INVALID_STATUS_FOOBAR"}
    )
    assert bad_res.status_code == 400
    err = bad_res.json()
    assert "error" in err
