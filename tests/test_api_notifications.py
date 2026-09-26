"""
Unit tests for Notifications (Twilio WhatsApp and SMS) API endpoints.
"""

from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


def test_notification_status_endpoint():
    """Verify Twilio notification status returns proper JSON configuration."""
    response = client.get("/api/notifications/status")
    assert response.status_code == 200
    data = response.json()
    assert "configured" in data
    assert "ready_for_live_delivery" in data
    assert "whatsapp_from" in data
    assert data["configured"] is True


def test_send_whatsapp_notification_valid():
    """Verify sending WhatsApp message formats phone and executes without crashing."""
    payload = {
        "phone": "+919876543210",
        "message": "VyaparMitra Peer Benchmark: Aap Lucknow mein 1st rank par hain!",
        "merchant_id": "M015"
    }
    response = client.post("/api/notifications/whatsapp", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "to" in data
    assert "whatsapp:+919876543210" in data["to"]


def test_send_whatsapp_missing_fields():
    """Verify validation error when phone or message is empty."""
    res1 = client.post("/api/notifications/whatsapp", json={"phone": "", "message": "hello"})
    assert res1.status_code == 400

    res2 = client.post("/api/notifications/whatsapp", json={"phone": "9876543210", "message": ""})
    assert res2.status_code == 400


def test_send_sms_notification_valid():
    """Verify sending SMS notification."""
    payload = {
        "phone": "9876543210",
        "message": "VyaparMitra Alert: Stock for Product P001 is critically low."
    }
    response = client.post("/api/notifications/sms", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "+919876543210" in data["to"]
