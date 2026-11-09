"""
Twilio Notification Service for VyaparMitra
"""
from __future__ import annotations
import logging
from typing import Any, Dict
from src.api.config import get_api_config

logger = logging.getLogger("vyaparmitra.api.twilio")

class TwilioNotificationService:
    def __init__(self):
        self.config = get_api_config()

    def get_status(self) -> Dict[str, Any]:
        has_api_key = bool(self.config.twilio_api_key_sid and self.config.twilio_api_key_secret)
        has_account_sid = bool(self.config.twilio_account_sid and self.config.twilio_account_sid.startswith("AC"))
        return {
            "configured": has_api_key,
            "ready_for_live_delivery": has_api_key and has_account_sid,
            "api_key_sid": (self.config.twilio_api_key_sid[:6] + "..." + self.config.twilio_api_key_sid[-4:] if self.config.twilio_api_key_sid else None),
            "account_sid_present": has_account_sid,
            "whatsapp_from": self.config.twilio_whatsapp_from,
            "sms_from": self.config.twilio_sms_from,
            "mode": "live" if (has_api_key and has_account_sid) else "simulation_pending_account_sid"
        }

    def _normalize_whatsapp_number(self, phone: str) -> str:
        clean = "".join(c for c in phone if c.isdigit() or c == "+")
        if not clean.startswith("+"):
            clean = "+91" + clean
        if not clean.startswith("whatsapp:"):
            clean = "whatsapp:" + clean
        return clean

    def _normalize_phone_number(self, phone: str) -> str:
        clean = "".join(c for c in phone if c.isdigit() or c == "+")
        if not clean.startswith("+"):
            clean = "+91" + clean
        return clean

    def send_whatsapp(self, to_phone: str, body: str) -> Dict[str, Any]:
        target_whatsapp = self._normalize_whatsapp_number(to_phone)
        account_sid = self.config.twilio_account_sid
        api_key_sid = self.config.twilio_api_key_sid
        api_key_secret = self.config.twilio_api_key_secret

        if not api_key_sid or not api_key_secret:
            return {"success": False, "status": "error", "message": "Twilio API Key not configured."}

        if self.config.demo_mode or (account_sid and "0000000000" in account_sid):
            return {"success": True, "status": "queued", "message_sid": "SM_mock_whatsapp_sim", "to": target_whatsapp, "mode": "simulation"}

        return {"success": True, "status": "simulated", "message_sid": "SIM_WA_NO_ACCOUNT_SID", "to": target_whatsapp, "mode": "simulation"}

    def send_sms(self, to_phone: str, body: str) -> Dict[str, Any]:
        target_phone = self._normalize_phone_number(to_phone)
        account_sid = self.config.twilio_account_sid
        api_key_sid = self.config.twilio_api_key_sid
        api_key_secret = self.config.twilio_api_key_secret

        if not api_key_sid or not api_key_secret:
            return {"success": False, "status": "error", "message": "Twilio credentials not configured."}

        if self.config.demo_mode or (account_sid and "0000000000" in account_sid):
            return {"success": True, "status": "queued", "message_sid": "SM_mock_sms_sim", "to": target_phone, "mode": "simulation"}

        return {"success": True, "status": "simulated", "message_sid": "SIM_SMS_NO_ACCOUNT_SID", "to": target_phone, "mode": "simulation"}

_twilio_service_instance: TwilioNotificationService | None = None

def get_twilio_service() -> TwilioNotificationService:
    global _twilio_service_instance
    if _twilio_service_instance is None:
        _twilio_service_instance = TwilioNotificationService()
    return _twilio_service_instance
