"""Runtime-safe paths for GUI assets in source and PyInstaller builds."""

import sys
from pathlib import Path


def asset_path(filename: str) -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS) / "src" / "gui" / "assets" / filename
    return Path(__file__).parent / "assets" / filename
