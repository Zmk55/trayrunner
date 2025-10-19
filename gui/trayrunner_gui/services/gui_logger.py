from __future__ import annotations
import logging
import os
from pathlib import Path

def get_logger(name="trayrunner_gui"):
    """Get or create a logger that writes to gui-debug.log"""
    base = Path.home() / ".local" / "state" / "trayrunner"
    base.mkdir(parents=True, exist_ok=True)
    log_path = base / "gui-debug.log"

    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    
    logger.setLevel(logging.DEBUG)

    fh = logging.FileHandler(log_path, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    fh.setFormatter(fmt)

    logger.addHandler(fh)
    logger.propagate = False
    logger.debug("=== GUI logger attached ===")
    return logger

def get_log_path():
    """Get path to the debug log file"""
    return str(Path.home() / ".local" / "state" / "trayrunner" / "gui-debug.log")
