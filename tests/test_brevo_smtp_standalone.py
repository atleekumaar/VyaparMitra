"""
Zero-external-dependency unit tests for Brevo SMTP and SQLite OTP logic.
Uses only Python standard library (unittest, smtplib, email, sqlite3, secrets).
"""

import os
import sqlite3
import unittest
from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock, patch

from src.api.services.email_service import BrevoEmailService


class TestBrevoSmtpStandalone(unittest.TestCase):
    def setUp(self):
        self.email_service = BrevoEmailService()
        self.test_email = "merchant@vyaparmitra.test"
        self.otp_code = "482910"
        self.merchant_name = "Rajesh Sharma"

    def test_status_unconfigured(self):
        """Verifies status defaults to simulation when credentials are absent."""
        self.email_service.config.brevo_smtp_user = ""
        self.email_service.config.brevo_smtp_password = ""
        status = self.email_service.get_status()
        self.assertFalse(status["configured"])
        self.assertEqual(status["mode"], "simulation")
        self.assertEqual(status["smtp_host"], "smtp-relay.brevo.com")
        self.assertEqual(status["smtp_port"], 587)

    def test_simulation_send(self):
        """Verifies send_otp_email safely returns simulated payload without credentials."""
        self.email_service.config.brevo_smtp_user = ""
        self.email_service.config.brevo_smtp_password = ""
        res = self.email_service.send_otp_email(
            to_email=self.test_email,
            otp_code=self.otp_code,
            merchant_name=self.merchant_name,
        )
        self.assertTrue(res["success"])
        self.assertEqual(res["status"], "simulated")
        self.assertEqual(res["to"], self.test_email)
        self.assertEqual(res["mode"], "simulation")

    @patch("smtplib.SMTP")
    def test_live_send_with_smtp_relay(self, mock_smtp):
        """Verifies STARTTLS, authentication, and message dispatch to Brevo SMTP."""
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server

        self.email_service.config.brevo_smtp_user = "brevo_user_id"
        self.email_service.config.brevo_smtp_password = "brevo_master_key"
        self.email_service.config.brevo_sender_email = "no-reply@vyaparmitra.com"
        self.email_service.config.brevo_sender_name = "VyaparMitra Security"

        res = self.email_service.send_otp_email(
            to_email=self.test_email,
            otp_code=self.otp_code,
            merchant_name=self.merchant_name,
        )

        self.assertTrue(res["success"])
        self.assertEqual(res["status"], "sent")
        self.assertEqual(res["to"], self.test_email)

        # Verify SMTP interaction
        mock_smtp.assert_called_with("smtp-relay.brevo.com", 587, timeout=12)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with("brevo_user_id", "brevo_master_key")
        mock_server.send_message.assert_called_once()

        # Verify MIME construction
        sent_msg = mock_server.send_message.call_args[0][0]
        self.assertEqual(sent_msg["Subject"], f"{self.otp_code} is your VyaparMitra Verification Code")
        self.assertIn("VyaparMitra Security", sent_msg["From"])
        self.assertEqual(sent_msg["To"], self.test_email)

        mock_server.quit.assert_called_once()

    def test_sqlite_otp_lifecycle(self):
        """Tests SQLite otps table creation, insertion, attempt tracking, and invalidation."""
        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row

        # Create schema
        conn.execute("""
            CREATE TABLE otps (
                id TEXT PRIMARY KEY,
                identifier TEXT NOT NULL,
                otp_code TEXT NOT NULL,
                purpose TEXT DEFAULT 'LOGIN',
                expires_at TEXT NOT NULL,
                attempts INTEGER DEFAULT 0,
                is_used INTEGER DEFAULT 0,
                created_at TEXT NOT NULL
            )
        """)
        conn.execute("CREATE INDEX idx_otps_lookup ON otps(identifier, is_used, expires_at)")

        now = datetime.now(timezone.utc)
        expires_at = (now + timedelta(minutes=10)).isoformat()
        now_str = now.isoformat()

        # Insert OTP
        conn.execute(
            "INSERT INTO otps (id, identifier, otp_code, purpose, expires_at, attempts, is_used, created_at) "
            "VALUES ('OTP_01', ?, ?, 'LOGIN', ?, 0, 0, ?)",
            (self.test_email, self.otp_code, expires_at, now_str),
        )
        conn.commit()

        # Query active OTP
        row = conn.execute(
            "SELECT * FROM otps WHERE identifier = ? AND is_used = 0 ORDER BY created_at DESC LIMIT 1",
            (self.test_email,),
        ).fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row["otp_code"], self.otp_code)
        self.assertEqual(row["attempts"], 0)
        self.assertEqual(row["is_used"], 0)

        # Increment attempts on failed verification
        conn.execute("UPDATE otps SET attempts = attempts + 1 WHERE id = ?", (row["id"],))
        conn.commit()

        updated = conn.execute("SELECT attempts FROM otps WHERE id = ?", (row["id"],)).fetchone()
        self.assertEqual(updated["attempts"], 1)

        # Mark as used upon successful verification
        conn.execute("UPDATE otps SET is_used = 1 WHERE id = ?", (row["id"],))
        conn.commit()

        active = conn.execute(
            "SELECT * FROM otps WHERE identifier = ? AND is_used = 0",
            (self.test_email,),
        ).fetchone()
        self.assertIsNone(active)

        conn.close()


if __name__ == "__main__":
    unittest.main()
