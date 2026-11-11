"""Pytest configuration for running the suite from any directory."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]# REVISAR QUE ESTO CONTIENE LA RUTA CORRECTA.
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
