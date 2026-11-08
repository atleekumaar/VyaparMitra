"""
Global test configuration & environment setup for VyaparMitra test suite.
"""
import os
import pytest
from src.api import config as api_config_module

os.environ["TWILIO_ACCOUNT_SID"] = "AC00000000000000000000000000000000"
os.environ["TWILIO_API_KEY_SID"] = "SK00000000000000000000000000000000"
os.environ["TWILIO_API_KEY_SECRET"] = "mock_secret_key_for_testing_123456"
os.environ["TWILIO_WHATSAPP_FROM"] = "whatsapp:+14155238886"
os.environ["TWILIO_SMS_FROM"] = "+14155238886"
os.environ["DEMO_MODE"] = "true"

@pytest.fixture(autouse=True)
def reset_api_config():
    """Ensure APIConfig singleton reflects the test environment."""
    api_config_module._config_instance = None
    yield
    api_config_module._config_instance = None
