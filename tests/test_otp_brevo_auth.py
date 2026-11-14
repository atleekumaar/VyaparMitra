"""
Unit and integration tests for Brevo SMTP and OTP Login Flow in VyaparMitra.
Covers:
- OTP generation and database storage
- Expiration and lockout validation
- Email delivery via BrevoEmailService (mocked SMTP)
- Successful OTP verification and JWT session generation
- Demo mode fallback and bypass
"""

import os
import unittest
from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from src.api.config import get_api_config
from src.api.db import get_db_connection, init_db
from src.api.main import app
from src.api.services.email_service import BrevoEmailService


class TestOtpBrevoAuth(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.client = TestClient(app)

    def setUp(self):
        self.test_email = "merchant.test@vyaparmitra.com"
        self.test_name = "Rajesh Sharma"
        # Clean any prior OTPs for test email
        conn = get_db_connection()
        conn.execute("DELETE FROM otps WHERE identifier = ?", (self.test_email,))
        conn.commit()
        conn.close()

    def test_request_otp_success(self):
        """Validates OTP request creates record in SQLite and returns proper payload."""
        response = self.client.post(
            "/api/auth/otp/send",
            json={
                "email": self.test_email,
                "name": self.test_name,
                "phone": "+919876543210",
            },
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["destination"], self.test_email)
        self.assertIn("expires_in_seconds", data)

        # Verify DB entry
        conn = get_db_connection()
        row = conn.execute(
            "SELECT * FROM otps WHERE identifier = ? AND is_used = 0",
            (self.test_email,),
        ).fetchone()
        conn.close()

        self.assertIsNotNone(row)
        self.assertEqual(len(row["otp_code"]), 6)
        self.assertTrue(row["otp_code"].isdigit())
        self.assertEqual(row["attempts"], 0)

    def test_request_otp_invalid_email(self):
        """Validates rejection of malformed email addresses."""
        response = self.client.post(
            "/api/auth/otp/send",
            json={"email": "invalid-format-email", "name": "Test"},
        )
        self.assertEqual(response.status_code, 400)

    def test_verify_otp_success(self):
        """Validates successful verification yields JWT and authenticates user."""
        # 1. Send OTP
        send_res = self.client.post(
            "/api/auth/otp/send",
            json={"email": self.test_email, "name": self.test_name},
        )
        self.assertEqual(send_res.status_code, 200)

        # Retrieve generated code from database
        conn = get_db_connection()
        otp_row = conn.execute(
            "SELECT otp_code FROM otps WHERE identifier = ? AND is_used = 0",
            (self.test_email,),
        ).fetchone()
        conn.close()
        self.assertIsNotNone(otp_row)
        otp_code = otp_row["otp_code"]

        # 2. Verify OTP
        verify_res = self.client.post(
            "/api/auth/otp/verify",
            json={"email": self.test_email, "otp": otp_code, "name": self.test_name},
        )
        self.assertEqual(verify_res.status_code, 200)
        auth_data = verify_res.json()

        self.assertIn("access_token", auth_data)
        self.assertEqual(auth_data["token_type"], "bearer")
        self.assertEqual(auth_data["user"]["email"], self.test_email)
        self.assertIn("sales:create", auth_data["permissions"])

        # Verify OTP is marked as used
        conn = get_db_connection()
        used_row = conn.execute(
            "SELECT is_used FROM otps WHERE identifier = ?",
            (self.test_email,),
        ).fetchone()
        conn.close()
        self.assertEqual(used_row["is_used"], 1)

    def test_verify_otp_invalid_code(self):
        """Validates that entering an incorrect code increments attempts and fails with 401."""
        self.client.post(
            "/api/auth/otp/send",
            json={"email": self.test_email, "name": self.test_name},
        )

        response = self.client.post(
            "/api/auth/otp/verify",
            json={"email": self.test_email, "otp": "999999"},
        )
        self.assertEqual(response.status_code, 401)

        conn = get_db_connection()
        row = conn.execute(
            "SELECT attempts FROM otps WHERE identifier = ?",
            (self.test_email,),
        ).fetchone()
        conn.close()
        self.assertEqual(row["attempts"], 1)

    def test_verify_otp_max_attempts_lockout(self):
        """Validates lockout after 5 consecutive incorrect attempts."""
        self.client.post(
            "/api/auth/otp/send",
            json={"email": self.test_email, "name": self.test_name},
        )

        conn = get_db_connection()
        conn.execute("UPDATE otps SET attempts = 5 WHERE identifier = ?", (self.test_email,))
        conn.commit()
        conn.close()

        response = self.client.post(
            "/api/auth/otp/verify",
            json={"email": self.test_email, "otp": "123456"},
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("locked", response.json()["detail"].lower())

    def test_verify_otp_expired(self):
        """Validates rejection when OTP has expired."""
        past_str = (datetime.now(timezone.utc) - timedelta(minutes=15)).isoformat()
        conn = get_db_connection()
        conn.execute(
            """
            INSERT INTO otps (id, identifier, otp_code, purpose, expires_at, attempts, is_used, created_at)
            VALUES ('OTP_EXP', ?, '123456', 'LOGIN', ?, 0, 0, ?)
            """,
            (self.test_email, past_str, past_str),
        )
        conn.commit()
        conn.close()

        response = self.client.post(
            "/api/auth/otp/verify",
            json={"email": self.test_email, "otp": "123456"},
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("expired", response.json()["detail"].lower())

    def test_demo_otp_bypass(self):
        """Validates 425026 demo code grants access in demo mode."""
        response = self.client.post(
            "/api/auth/otp/verify",
            json={"email": "demo.merchant@vyaparmitra.com", "otp": "425026", "name": "Demo User"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("access_token", data)
        self.assertEqual(data["user"]["role"], "owner")

    @patch("smtplib.SMTP")
    def test_brevo_email_service_send(self, mock_smtp_class):
        """Validates BrevoEmailService configures STARTTLS, logins, and sends MIME message."""
        mock_server = MagicMock()
        mock_smtp_class.return_value = mock_server

        service = BrevoEmailService()
        # Mock credentials
        service.config.brevo_smtp_user = "brevo_user_login"
        service.config.brevo_smtp_password = "brevo_key_secret"

        result = service.send_otp_email(
            to_email="customer@example.com",
            otp_code="582194",
            merchant_name="Sharma Kirana",
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["status"], "sent")
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with("brevo_user_login", "brevo_key_secret")
        mock_server.send_message.assert_called_once()
        mock_server.quit.assert_called_once()


if __name__ == "__main__":
    unittest.main()
