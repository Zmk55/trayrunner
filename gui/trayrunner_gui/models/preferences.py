"""User preferences management"""
from __future__ import annotations
from pathlib import Path
import json
from typing import Dict, Any

PREFS_PATH = Path.home() / ".config/trayrunner/gui_prefs.json"

def load_prefs() -> Dict[str, Any]:
    """Load user preferences from disk"""
    if PREFS_PATH.exists():
        try:
            return json.loads(PREFS_PATH.read_text("utf-8"))
        except Exception:
            pass
    # Default preferences
    return {"reload_after_save": True}

def save_prefs(prefs: Dict[str, Any]) -> None:
    """Save user preferences to disk"""
    PREFS_PATH.parent.mkdir(parents=True, exist_ok=True)
    PREFS_PATH.write_text(json.dumps(prefs, indent=2), "utf-8")
