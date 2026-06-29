"""Thiết lập import path cho app Streamlit."""

import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = APP_DIR.parent

for path in (ROOT_DIR, APP_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))
