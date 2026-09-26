"""
Notifications API Routes for VyaparMitra.
Provides endpoints to trigger WhatsApp weekly digests and SMS merchant alerts via Twilio.
"""

from __future__ import annotations

from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.api.services.twilio_service import get_twilio_service

router = APIRouter(prefix="/notifications", tags=["Notifications"])


class SendWhatsAppRequest(BaseModel):
    phone: str = Field(..., description="Recipient phone number with country code, e.g. +919876543210")
    message: str = Field(..., description="Message body or WhatsApp Weekly Digest text")
    merchant_id: Optional[str] = Field(default="M001", description="Merchant ID for reference")


class SendSMSRequest(BaseModel):
    phone: str = Field(..., description="Recipient phone number")
    message: str = Field(..., description="SMS message text")


@router.get("/status")
def get_notification_status():
    """Check Twilio SMS and WhatsApp integration status."""
    service = get_twilio_service()
    return service.get_status()


@router.post("/whatsapp")
def send_whatsapp_notification(payload: SendWhatsAppRequest):
    """
    Send WhatsApp weekly digest or real-time alert to merchant via Twilio.
    Supports live delivery when TWILIO_ACCOUNT_SID is set, or verified simulation with clear feedback.
    """
    if not payload.phone.strip():
        raise HTTPException(status_code=400, detail="Phone number is required")
    if not payload.message.strip():
        raise HTTPException(status_code=400, detail="Message content cannot be empty")

    service = get_twilio_service()
    result = service.send_whatsapp(to_phone=payload.phone, body=payload.message)
    return result


@router.post("/sms")
def send_sms_notification(payload: SendSMSRequest):
    """Send SMS notification to merchant."""
    if not payload.phone.strip():
        raise HTTPException(status_code=400, detail="Phone number is required")
    if not payload.message.strip():
        raise HTTPException(status_code=400, detail="Message content cannot be empty")

    service = get_twilio_service()
    result = service.send_sms(to_phone=payload.phone, body=payload.message)
    return result
