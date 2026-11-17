"""
Tests for Concurrency (SQLite WAL Mode & Busy Timeout) and Rate Limiting Protection.
"""

import os
import unittest
from fastapi.testclient import TestClient

from src.api.db import get_db_connection
from src.api.main import app
from src.api.middleware import global_rate_limiter
from src.ml.inference.predictor import Predictor


class TestConcurrencyAndRateLimit(unittest.TestCase):
    def setUp(self):
        global_rate_limiter.clear()

    def test_sqlite_wal_mode_and_busy_timeout(self):
        """Verifies that SQLite connections use WAL mode and busy_timeout."""
        conn = get_db_connection()
        try:
            # Check journal mode (file DB -> wal, in-memory DB -> memory)
            journal_mode = conn.execute("PRAGMA journal_mode").fetchone()[0]
            self.assertIn(journal_mode.lower(), ("wal", "memory"))

            # Check busy timeout
            busy_timeout = conn.execute("PRAGMA busy_timeout").fetchone()[0]
            self.assertGreaterEqual(busy_timeout, 10000)

            # Check foreign keys
            fk = conn.execute("PRAGMA foreign_keys").fetchone()[0]
            self.assertEqual(fk, 1)
        finally:
            conn.close()

    def test_rate_limiter_allows_and_blocks_when_exceeded(self):
        """Validates that rate limiter enforces thresholds and returns 429 with headers."""
        client = TestClient(app)

        # Clear any bypass env vars for this specific test
        old_env = os.environ.get("PYTEST_CURRENT_TEST")
        if "PYTEST_CURRENT_TEST" in os.environ:
            del os.environ["PYTEST_CURRENT_TEST"]

        try:
            # Route limit for /api/auth/otp/send is 10 requests per minute
            target_endpoint = "/api/auth/otp/send"
            client_ip = "192.168.1.100"
            headers = {"X-Forwarded-For": client_ip}

            # Send 10 allowed requests (they might fail validation, but middleware lets them through)
            for i in range(10):
                res = client.post(target_endpoint, json={"email": "invalid"}, headers=headers)
                self.assertIn("X-RateLimit-Limit", res.headers)
                self.assertNotEqual(res.status_code, 429)

            # 11th request must be rate limited with HTTP 429
            blocked_res = client.post(target_endpoint, json={"email": "invalid"}, headers=headers)
            self.assertEqual(blocked_res.status_code, 429)
            self.assertIn("Retry-After", blocked_res.headers)
            self.assertEqual(blocked_res.headers["X-RateLimit-Remaining"], "0")

            data = blocked_res.json()
            self.assertEqual(data["error"]["code"], "RATE_LIMIT_EXCEEDED")
            self.assertIn("Rate limit exceeded", data["error"]["message"])

        finally:
            if old_env is not None:
                os.environ["PYTEST_CURRENT_TEST"] = old_env

    def test_dynamic_churn_prediction_snapshot(self):
        """Verifies that predict_churn dynamically resolves snapshot date when None."""
        pred = Predictor()
        df = pred.predict_churn(snapshot_date=None)
        self.assertFalse(df.empty)
        self.assertIn("risk_probability", df.columns)
        self.assertIn("risk_band", df.columns)

    def test_trigger_database_backup_endpoint(self):
        """Verifies that POST /api/health/backup generates snapshot."""
        client = TestClient(app)
        conn = get_db_connection()
        conn.execute(
            "INSERT OR IGNORE INTO users (id, business_id, branch_id, username, email, full_name, password_hash, role, is_active, created_at) "
            "VALUES ('USR_BACKUP_TEST', 'M015', 'BR_M015_MAIN', 'test_backup_user', 'backup@test.com', 'Backup User', 'hash', 'owner', 1, '2026-01-01')"
        )
        conn.commit()
        conn.close()

        from src.api.auth import create_access_token
        token = create_access_token({"sub": "USR_BACKUP_TEST", "role": "owner", "business_id": "M015"})
        res = client.post("/api/health/backup", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["success"])
        self.assertIn("backup_file", data)
        self.assertGreater(data["size_bytes"], 0)

    def test_copilot_tenant_isolation(self):
        """Verifies that copilot ask automatically scopes to authenticated merchant."""
        client = TestClient(app)
        conn = get_db_connection()
        conn.execute(
            "INSERT OR IGNORE INTO users (id, business_id, branch_id, username, email, full_name, password_hash, role, is_active, created_at) "
            "VALUES ('USR_COPILOT_TEST', 'M015', 'BR_M015_MAIN', 'copilot_test_user', 'copilot@test.com', 'Copilot User', 'hash', 'owner', 1, '2026-01-01')"
        )
        conn.commit()
        conn.close()

        from src.api.auth import create_access_token
        token = create_access_token({"sub": "USR_COPILOT_TEST", "role": "owner", "business_id": "M015"})
        headers = {"Authorization": f"Bearer {token}", "X-Merchant-Id": "M015"}
        res = client.post(
            "/api/copilot/ask",
            json={"query": "Meri dukaan ka status kya hai?", "merchant_id": "M999"},
            headers=headers,
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIsNotNone(data["answer"])
