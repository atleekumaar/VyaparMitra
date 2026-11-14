"""
Live verification script for Brevo SMTP integration in VyaparMitra.
Sends a live OTP test email to astravedaai625@gmail.com using the credentials in .env.
"""

import sys
import os
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Load .env into os.environ
env_path = PROJECT_ROOT / ".env"
if env_path.exists():
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ[k.strip()] = v.strip().strip('"').strip("'")

from src.api.services.email_service import BrevoEmailService

def main():
    service = BrevoEmailService()
    status = service.get_status()
    print("Brevo Service Status:", status)
    
    target_email = "astravedaai625@gmail.com"
    test_otp = "849201"
    
    print(f"\nAttempting live SMTP dispatch to {target_email} with OTP {test_otp}...")
    result = service.send_otp_email(
        to_email=target_email,
        otp_code=test_otp,
        merchant_name="AstraVeda Merchant"
    )
    print("Result:", result)
    
    if result.get("success") and result.get("mode") == "live":
        print("\nSUCCESS: Live Brevo SMTP OTP email dispatched successfully!")
        return 0
    else:
        print(f"\nFAILED or fallback mode: {result}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
