"""
Environment compatibility checks
"""

from pathlib import Path
import subprocess
from typing import Tuple


def check_tray_support() -> Tuple[bool, str]:
    """Check if system tray support is available"""
    
    # Check for common tray implementations
    indicators = [
        "libayatana-appindicator3.so",
        "libappindicator3.so"
    ]
    
    for lib in indicators:
        try:
            result = subprocess.run(
                ["ldconfig", "-p"],
                capture_output=True,
                text=True
            )
            if lib in result.stdout:
                return (True, "Tray support available")
        except:
            pass
    
    return (False, "Install: sudo apt install libayatana-appindicator3-1")


def show_tray_hint_once():
    """Show one-time hint about tray support if missing"""
    hint_file = Path.home() / ".config" / "trayrunner" / ".tray_hint_shown"
    
    if hint_file.exists():
        return
    
    supported, message = check_tray_support()
    if not supported:
        # Show QMessageBox with hint
        from PySide6.QtWidgets import QMessageBox
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Optional: Tray Support")
        msg.setText("TrayRunner can integrate with system tray.")
        msg.setInformativeText(message)
        msg.exec()
        
        # Mark as shown
        hint_file.parent.mkdir(parents=True, exist_ok=True)
        hint_file.write_text("shown")
