import sys
from pathlib import Path

# Add project root directory to Python path for serverless imports
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.api.main import app

# Handler for Vercel serverless function
handler = app
