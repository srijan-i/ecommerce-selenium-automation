"""Central configuration. Every value can be overridden with an environment variable."""
import os
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
SCREENSHOT_DIR = ROOT_DIR / "screenshots"
REPORT_DIR = ROOT_DIR / "reports"

BASE_URL = os.getenv("BASE_URL", "https://automationexercise.com").rstrip("/")
BROWSER = os.getenv("BROWSER", "chrome").lower()            # chrome | firefox | edge
HEADLESS = os.getenv("HEADLESS", "false").lower() == "true"
DATA_FILE = os.getenv("DATA_FILE", "test_data.json")         # or test_data.xlsx

EXPLICIT_WAIT = int(os.getenv("EXPLICIT_WAIT", "20"))
PAGE_LOAD_TIMEOUT = int(os.getenv("PAGE_LOAD_TIMEOUT", "45"))

STEP_DELAY = float(os.getenv("STEP_DELAY", "0"))   # seconds to pause before every action
