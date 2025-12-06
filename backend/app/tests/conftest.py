import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[2]

if str(BACKEND_DIR) not in sys.path:
    sys.path.append(str(BACKEND_DIR))
