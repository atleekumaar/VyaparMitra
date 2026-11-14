"""
Brevo (Sendinblue) SMTP Email Service for VyaparMitra.
Provides reliable, secure transactional email delivery for OTP verification and merchant alerts.
"""

from __future__ import annotations

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Dict, Optional

from src.api.config import get_api_config

logger = logging.getLogger("vyaparmitra.api.email")


class BrevoEmailService:
    """Handles transactional email delivery using Brevo SMTP relay."""

    def __init__(self):
        self.config = get_api_config()

    def get_status(self) -> Dict[str, Any]:
        """Returns the configuration status of the Brevo SMTP relay."""
        has_credentials = bool(self.config.brevo_smtp_user and self.config.brevo_smtp_password)
        return {
            "configured": has_credentials,
            "smtp_host": self.config.brevo_smtp_host,
            "smtp_port": self.config.brevo_smtp_port,
            "sender_email": self.config.brevo_sender_email,
            "sender_name": self.config.brevo_sender_name,
            "mode": "live" if has_credentials else "simulation",
        }

    def send_otp_email(
        self,
        to_email: str,
        otp_code: str,
        merchant_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Dispatches a 6-digit OTP verification email via Brevo SMTP relay.
        
        If Brevo credentials are not configured or the connection fails in demo mode,
        it safely logs the event and returns a simulation payload so testing is never blocked.
        """
        clean_email = to_email.strip().lower()
        display_name = (merchant_name or "Merchant").strip()
        expiry_min = self.config.otp_expiry_minutes

        has_credentials = bool(self.config.brevo_smtp_user and self.config.brevo_smtp_password)

        if not has_credentials:
            logger.info(
                f"[SIMULATION] Brevo SMTP not configured. OTP for {clean_email}: {otp_code} (Valid for {expiry_min}m)"
            )
            return {
                "success": True,
                "status": "simulated",
                "to": clean_email,
                "message": f"Simulation mode: OTP {otp_code} generated for {clean_email}.",
                "mode": "simulation",
            }

        # Build Multipart Email (Plain Text + Rich HTML)
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"{otp_code} is your VyaparMitra Verification Code"
        msg["From"] = f"{self.config.brevo_sender_name} <{self.config.brevo_sender_email}>"
        msg["To"] = clean_email

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
          
          <!-- Header Banner -->
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

          <!-- Body Content -->
          <tr>
            <td style="padding: 32px 32px 24px 32px;">
              <h2 style="margin: 0 0 8px 0; font-size: 18px; font-weight: 600; color: #0f172a;">
                Namaste, {display_name} Ji
              </h2>
              <p style="margin: 0 0 24px 0; font-size: 14px; line-height: 1.6; color: #475569;">
                Here is your 6-digit one-time password (OTP) to securely sign in to your merchant dashboard:
              </p>

              <!-- OTP Code Display Card -->
              <div style="background-color: #eff6ff; border: 2px dashed #93c5fd; border-radius: 12px; padding: 20px; text-align: center; margin-bottom: 24px;">
                <div style="font-size: 34px; font-weight: 800; letter-spacing: 10px; color: #1d4ed8; font-family: 'Courier New', Courier, monospace; margin-left: 10px;">
                  {otp_code}
                </div>
                <div style="font-size: 12px; color: #3b82f6; font-weight: 600; margin-top: 8px;">
                  Valid for {expiry_min} minutes only
                </div>
              </div>

              <!-- Security Advisory -->
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

          <!-- Footer -->
          <tr>
            <td style="background-color: #f1f5f9; padding: 20px 32px; border-top: 1px solid #e2e8f0; text-align: center;">
              <p style="margin: 0 0 4px 0; font-size: 11px; color: #64748b;">
                Sent securely via Brevo SMTP Relay &bull; VyaparMitra AI
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
            }
        except smtplib.SMTPAuthenticationError as auth_err:
            logger.error(f"Brevo SMTP authentication failed: {auth_err}")
            err_str = str(auth_err)
            if "525" in err_str or "unauthorized ip" in err_str.lower():
                user_msg = (
                    "Brevo SMTP rejected connection: 525 Unauthorized IP address. "
                    "In Brevo Dashboard > Settings > Security > Authorized IPs: authorize your outbound IP "
                    "or click 'Validate your IP address' in the confirmation email sent by Brevo."
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
            logger.error(f"Failed to send email via Brevo SMTP: {exc}")
            if self.config.demo_mode:
                return {
                    "success": True,
                    "status": "simulated_error_fallback",
                    "to": clean_email,
                    "message": f"SMTP network error ({exc}). Falling back to demo mode. OTP: {otp_code}",
                    "mode": "simulation",
                }
            return {
                "success": False,
                "status": "network_error",
                "message": f"Failed to deliver email via Brevo SMTP: {str(exc)}",
            }


_email_service_instance: Optional[BrevoEmailService] = None


def get_email_service() -> BrevoEmailService:
    """Singleton getter for BrevoEmailService."""
    global _email_service_instance
    if _email_service_instance is None:
        _email_service_instance = BrevoEmailService()
    return _email_service_instance
