"""
Reload coordinator - communicates with tray app to trigger config reload
"""

from PySide6.QtNetwork import QLocalSocket
from PySide6.QtCore import QStandardPaths
import os
import shutil
import subprocess
import json
import time
from typing import Tuple


def _sock_path() -> str:
    """Get path to reload socket"""
    base = os.path.join(
        QStandardPaths.writableLocation(QStandardPaths.AppDataLocation) or
        os.path.expanduser("~/.local/state/trayrunner")
    )
    return os.path.join(base, "reload.sock")


def _reload_via_socket(timeout_ms: int = 500) -> Tuple[bool, str]:
    """Try to reload via socket IPC"""
    sock_path = _sock_path()
    
    # Check if socket exists
    if not os.path.exists(sock_path):
        return (False, "socket not found")
    
    socket = QLocalSocket()
    socket.connectToServer(sock_path)
    
    if not socket.waitForConnected(timeout_ms):
        return (False, f"connect timeout: {socket.errorString()}")
    
    # Send reload command
    socket.write(b"RELOAD")
    socket.flush()
    
    if not socket.waitForReadyRead(timeout_ms):
        socket.disconnectFromServer()
        return (False, "no response from tray")
    
    try:
        response_data = bytes(socket.readAll()).decode("utf-8")
        response = json.loads(response_data)
        socket.disconnectFromServer()
        
        if response.get("ok"):
            return (True, "reloaded via socket")
        else:
            return (False, "tray reload failed")
    except Exception as e:
        socket.disconnectFromServer()
        return (False, f"bad response: {e}")


def _which_trayrunner() -> str | None:
    """Find trayrunner executable on PATH"""
    return shutil.which("trayrunner")


def _reload_via_cli() -> Tuple[bool, str]:
    """Fallback: reload via CLI command"""
    exe = _which_trayrunner()
    if not exe:
        return (False, "trayrunner not found on PATH")
    
    try:
        proc = subprocess.run(
            [exe, "--reload"],
            capture_output=True,
            text=True,
            timeout=2
        )
        msg = (proc.stdout or proc.stderr).strip() or "reloaded via CLI"
        return (proc.returncode == 0, msg)
    except subprocess.TimeoutExpired:
        return (False, "CLI reload timeout")
    except Exception as e:
        return (False, f"CLI reload error: {e}")


def reload_trayrunner() -> Tuple[bool, str]:
    """
    Request tray app to reload configuration.
    
    Tries socket IPC first, falls back to CLI if unavailable.
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    # Try socket first (fast, works in AppImage)
    ok, msg = _reload_via_socket()
    if ok:
        return (True, msg)
    
    # Socket failed - try CLI fallback
    ok_cli, msg_cli = _reload_via_cli()
    if ok_cli:
        return (True, msg_cli)
    
    # Both failed
    return (False, f"socket: {msg}; CLI: {msg_cli}")


# Backwards compatibility alias
try_reload = reload_trayrunner


def is_trayrunner_running() -> bool:
    """
    Check if TrayRunner is currently running by checking for socket
    
    Returns:
        True if socket exists, False otherwise
    """
    return os.path.exists(_sock_path())


def get_trayrunner_status() -> Tuple[bool, str]:
    """
    Get TrayRunner status information
    
    Returns:
        Tuple of (is_running, status_message)
    """
    if is_trayrunner_running():
        return (True, "TrayRunner running (socket available)")
    else:
        return (False, "TrayRunner not running (socket not found)")


class ReloadManager:
    """Manages TrayRunner reload operations"""
    
    def __init__(self):
        self.last_reload_result = None
        self.last_reload_time = None
    
    def reload_config(self) -> Tuple[bool, str]:
        """
        Reload TrayRunner configuration and cache result
        
        Returns:
            Tuple of (success, message)
        """
        success, message = reload_trayrunner()
        
        self.last_reload_result = (success, message)
        self.last_reload_time = time.time()
        
        return success, message
    
    def get_last_reload_result(self) -> Tuple[bool, str]:
        """Get the result of the last reload attempt"""
        return self.last_reload_result or (False, "No reload attempted yet")
    
    def can_reload(self) -> bool:
        """Check if reload is possible (TrayRunner is running)"""
        return is_trayrunner_running()


# Global reload manager instance
reload_manager = ReloadManager()