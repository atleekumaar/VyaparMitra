"""
Brevo (Sendinblue) Email Service for VyaparMitra.
Provides reliable, secure transactional email delivery for OTP verification:
1. Brevo HTTP REST API v3 (Port 443 / HTTPS) - Ultra-fast (~200ms), firewall-proof, works on Render Free Tier.
2. Brevo SMTP Relay (Port 587 / STARTTLS) - Standard SMTP fallback for local development.
3. Offline Simulation Mode - Graceful fallback when running offline or in demo mode.
"""

from __future__ import annotations

import json
import logging
import smtplib
import urllib.error
import urllib.request
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Dict, Optional

from src.api.config import get_api_config

logger = logging.getLogger("vyaparmitra.api.email")


class BrevoEmailService:
    """Handles transactional email delivery using Brevo HTTP REST API or SMTP relay."""

    def __init__(self):
        self.config = get_api_config()

    def _get_api_key(self) -> str:
        """Retrieves Brevo API v3 key from config or detects xkeysib- prefix."""
        if self.config.brevo_api_key:
            return self.config.brevo_api_key.strip()
        if self.config.brevo_smtp_password and self.config.brevo_smtp_password.startswith("xkeysib-"):
            return self.config.brevo_smtp_password.strip()
        return ""

    def get_status(self) -> Dict[str, Any]:
        """Returns the configuration status of the Brevo Email service."""
        api_key = self._get_api_key()
        has_smtp = bool(self.config.brevo_smtp_user and self.config.brevo_smtp_password)
        is_live = bool(api_key or has_smtp)

        channel = "http_api" if api_key else ("smtp_relay" if has_smtp else "simulation")
        return {
            "configured": is_live,
            "channel": channel,
            "smtp_host": self.config.brevo_smtp_host,
            "smtp_port": self.config.brevo_smtp_port,
            "sender_email": self.config.brevo_sender_email,
            "sender_name": self.config.brevo_sender_name,
            "mode": "live" if is_live else "simulation",
        }

    def _send_via_http_api(
        self,
        to_email: str,
        otp_code: str,
        display_name: str,
        plain_text: str,
        html_content: str,
        api_key: str,
    ) -> Dict[str, Any]:
        """
        Dispatches OTP email via Brevo HTTP REST API v3 over HTTPS (Port 443).
        Bypasses cloud provider SMTP port 587 firewall blocks (e.g. on Render Free Tier).
        """
        url = "https://api.brevo.com/v3/smtp/email"
        payload = {
            "sender": {
                "name": self.config.brevo_sender_name,
                "email": self.config.brevo_sender_email,
            },
            "to": [
                {
                    "email": to_email,
                    "name": display_name,
                }
            ],
            "subject": f"{otp_code} is your VyaparMitra Verification Code",
            "htmlContent": html_content,
            "textContent": plain_text,
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "api-key": api_key,
                "content-type": "application/json",
                "accept": "application/json",
            },
            method="POST",
        )

        try:
            logger.info(f"Dispatching OTP to {to_email} via Brevo HTTP REST API (port 443)...")
            with urllib.request.urlopen(req, timeout=8) as response:
                resp_data = json.loads(response.read().decode("utf-8"))
                logger.info(f"Successfully delivered OTP to {to_email} via Brevo HTTP API: {resp_data}")
                return {
                    "success": True,
                    "status": "sent",
                    "to": to_email,
                    "message": f"Verification code sent to {to_email}.",
                    "mode": "live",
                    "channel": "http_api",
                    "message_id": resp_data.get("messageId"),
                }
        except urllib.error.HTTPError as http_err:
            raw_err = http_err.read().decode("utf-8")
            logger.error(f"Brevo HTTP API returned HTTP {http_err.code}: {raw_err}")

            if "not authorized for resource" in raw_err:
                user_msg = (
                    "Brevo API key permission denied: Ensure your API key has 'Full' access or 'Transactional email: All' "
                    "permissions in Brevo Dashboard > Settings > SMTP & API > API Keys."
                )
            elif http_err.code == 401:
                user_msg = "Invalid Brevo API Key. Please verify BREVO_API_KEY in environment variables."
            else:
                user_msg = f"Brevo HTTP API error ({http_err.code}): {raw_err}"

            return {
                "success": False,
                "status": "permission_denied" if http_err.code in (401, 403) else "api_error",
                "message": user_msg,
            }
        except Exception as exc:
            logger.error(f"Brevo HTTP API network error: {exc}")
            return {
                "success": False,
                "status": "network_error",
                "message": f"Brevo HTTP network error: {str(exc)}",
            }

    def send_otp_email(
        self,
        to_email: str,
        otp_code: str,
        merchant_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Dispatches a 6-digit OTP verification email.
        Tries Brevo HTTP REST API v3 first (port 443), falls back to SMTP relay (port 587),
        and safely activates simulation mode if credentials are absent or fail in demo mode.
        """
        clean_email = to_email.strip().lower()
        display_name = (merchant_name or "Merchant").strip()
        expiry_min = self.config.otp_expiry_minutes

        api_key = self._get_api_key()
        has_smtp = bool(self.config.brevo_smtp_user and self.config.brevo_smtp_password)

        if not api_key and not has_smtp:
            logger.info(
                f"[SIMULATION] Brevo credentials not configured. OTP for {clean_email}: {otp_code} (Valid for {expiry_min}m)"
            )
            return {
                "success": True,
                "status": "simulated",
                "to": clean_email,
                "message": f"Simulation mode: OTP {otp_code} generated for {clean_email}.",
                "mode": "simulation",
            }

        # Plain-text and Rich HTML templates
        plain_text = (
            f"Namaste {display_name},\n\n"
            f"Your one-time verification code for VyaparMitra Command Center is:\n\n"
            f"    {otp_code}\n\n"
            f"This code will expire in {expiry_min} minutes.\n"
            f"For your account security, never share this OTP with anyone.\n\n"
            f"If you did not request this login code, you can safely ignore this email.\n\n"
            f"— Team VyaparMitra (व्यापारमित्र)"
        )

        html_content = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>VyaparMitra Verification Code</title>
</head>
<body style="margin: 0; padding: 0; background-color: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #1e293b;">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color: #f8fafc; padding: 40px 15px;">
    <tr>
      <td align="center">
        <table role="presentation" width="100%" style="max-width: 520px; background-color: #ffffff; border-radius: 16px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); overflow: hidden;">
          <tr>
            <td style="background-color: #2563eb; padding: 24px 32px; text-align: left;">
              <table role="presentation" cellspacing="0" cellpadding="0">
                <tr>
                  <td style="width: 36px; height: 36px; background-color: #ffffff; border-radius: 8px; text-align: center; vertical-align: middle; font-weight: bold; font-size: 16px; color: #2563eb;">
                    VM
                  </td>
                  <td style="padding-left: 12px; color: #ffffff; font-size: 20px; font-weight: 700; letter-spacing: -0.5px;">
                    Vyapar<span style="color: #93c5fd;">Mitra</span>
                  </td>
                </tr>
              </table>
              <p style="margin: 6px 0 0 0; color: #bfdbfe; font-size: 12px; font-weight: 500;">
                Merchant Intelligence & Copilot Command Center
              </p>
            </td>
          </tr>
          <tr>
            <td style="padding: 32px 32px 24px 32px;">
              <h2 style="margin: 0 0 8px 0; font-size: 18px; font-weight: 600; color: #0f172a;">
                Namaste, {display_name} Ji
              </h2>
              <p style="margin: 0 0 24px 0; font-size: 14px; line-height: 1.6; color: #475569;">
                Here is your 6-digit one-time password (OTP) to securely sign in to your merchant dashboard:
              </p>
              <div style="background-color: #eff6ff; border: 2px dashed #93c5fd; border-radius: 12px; padding: 20px; text-align: center; margin-bottom: 24px;">
                <div style="font-size: 34px; font-weight: 800; letter-spacing: 10px; color: #1d4ed8; font-family: 'Courier New', Courier, monospace; margin-left: 10px;">
                  {otp_code}
                </div>
                <div style="font-size: 12px; color: #3b82f6; font-weight: 600; margin-top: 8px;">
                  Valid for {expiry_min} minutes only
                </div>
              </div>
              <table role="presentation" width="100%" style="background-color: #fffbeb; border-radius: 8px; border: 1px solid #fef3c7; padding: 12px 16px; margin-bottom: 24px;">
                <tr>
                  <td style="font-size: 12px; color: #92400e; line-height: 1.5;">
                    🔒 <strong>Security Notice:</strong> VyaparMitra support will never ask for this code over phone, email, or WhatsApp. Do not share it with anyone.
                  </td>
                </tr>
              </table>
              <p style="margin: 0; font-size: 13px; line-height: 1.5; color: #64748b;">
                If you did not initiate this login request, please verify your account security immediately.
              </p>
            </td>
          </tr>
          <tr>
            <td style="background-color: #f1f5f9; padding: 20px 32px; border-top: 1px solid #e2e8f0; text-align: center;">
              <p style="margin: 0 0 4px 0; font-size: 11px; color: #64748b;">
                Sent securely via Brevo Delivery &bull; VyaparMitra AI
              </p>
              <p style="margin: 0; font-size: 11px; color: #94a3b8;">
                &copy; 2026 VyaparMitra. Empowering India's Retail Merchants.
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""

        # PRIMARY: Attempt Brevo HTTP REST API v3 over HTTPS (Port 443)
        if api_key:
            http_res = self._send_via_http_api(
                to_email=clean_email,
                otp_code=otp_code,
                display_name=display_name,
                plain_text=plain_text,
                html_content=html_content,
                api_key=api_key,
            )
            if http_res.get("success"):
                return http_res

            # If HTTP API returned an authorization error, do not silently swallow in live mode
            if not self.config.demo_mode and not has_smtp:
                return http_res
            if self.config.demo_mode and not has_smtp:
                return {
                    "success": True,
                    "status": "simulated_api_fallback",
                    "to": clean_email,
                    "message": f"{http_res.get('message')} (Demo fallback OTP: {otp_code})",
                    "mode": "simulation",
                }

        # SECONDARY: Attempt Brevo SMTP Relay (Port 587)
        if not has_smtp:
            return {
                "success": False,
                "status": "unconfigured",
                "message": "Neither Brevo API Key nor SMTP credentials are fully configured.",
            }

        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"{otp_code} is your VyaparMitra Verification Code"
        msg["From"] = f"{self.config.brevo_sender_name} <{self.config.brevo_sender_email}>"
        msg["To"] = clean_email
        msg.attach(MIMEText(plain_text, "plain", "utf-8"))
        msg.attach(MIMEText(html_content, "html", "utf-8"))

        try:
            logger.info(f"Connecting to Brevo SMTP {self.config.brevo_smtp_host}:{self.config.brevo_smtp_port}...")
            server = smtplib.SMTP(self.config.brevo_smtp_host, self.config.brevo_smtp_port, timeout=12)
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(self.config.brevo_smtp_user, self.config.brevo_smtp_password)
            server.send_message(msg)
            server.quit()
            logger.info(f"Successfully sent OTP email to {clean_email} via Brevo SMTP.")
            return {
                "success": True,
                "status": "sent",
                "to": clean_email,
                "message": f"Verification code sent to {clean_email}.",
                "mode": "live",
                "channel": "smtp_relay",
            }
        except smtplib.SMTPAuthenticationError as auth_err:
            logger.error(f"Brevo SMTP authentication failed: {auth_err}")
            err_str = str(auth_err)
            if "525" in err_str or "unauthorized ip" in err_str.lower():
                user_msg = (
                    "Brevo SMTP rejected connection: 525 Unauthorized IP address. "
                    "In Brevo Dashboard > Settings > Security > Authorized IPs: authorize your outbound IP "
                    "or deactivate 'Blocking unauthorized IP addresses'."
                )
            else:
                user_msg = "Brevo SMTP authentication failed. Please verify BREVO_SMTP_USER and BREVO_SMTP_PASSWORD."

            if self.config.demo_mode:
                return {
                    "success": True,
                    "status": "simulated_auth_fallback",
                    "to": clean_email,
                    "message": f"{user_msg} Falling back to demo mode. OTP: {otp_code}",
                    "mode": "simulation",
                }
            return {
                "success": False,
                "status": "auth_error",
                "message": user_msg,
            }
        except Exception as exc:
            err_msg = str(exc)
            logger.error(f"Failed to send email via Brevo SMTP: {exc}")
            if "timed out" in err_msg.lower():
                user_msg = (
                    "SMTP connection to port 587 timed out. Note: Cloud providers like Render Free Tier block outbound SMTP ports (587, 465, 25). "
                    "Please configure BREVO_API_KEY to send via Brevo HTTP REST API over HTTPS (port 443)."
                )
            else:
                user_msg = f"Failed to deliver email via Brevo SMTP: {err_msg}"

            if self.config.demo_mode:
                return {
                    "success": True,
                    "status": "simulated_error_fallback",
                    "to": clean_email,
                    "message": f"{user_msg} Falling back to demo mode. OTP: {otp_code}",
                    "mode": "simulation",
                }
            return {
                "success": False,
                "status": "network_error",
                "message": user_msg,
            }


_email_service_instance: Optional[BrevoEmailService] = None


def get_email_service() -> BrevoEmailService:
    """Singleton getter for BrevoEmailService."""
    global _email_service_instance
    if _email_service_instance is None:
        _email_service_instance = BrevoEmailService()
    return _email_service_instance
