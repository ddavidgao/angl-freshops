from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "build" / "latest"

if str(BUILD) not in sys.path:
    sys.path.insert(0, str(BUILD))

from build_delivery_promise import build_delivery_promise  # noqa: E402,F401
