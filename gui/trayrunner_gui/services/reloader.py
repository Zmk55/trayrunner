"""
Service for reloading TrayRunner configuration
"""

import shutil
import subprocess
import sys
from typing import Tuple


def try_reload() -> Tuple[bool, str]:
    """
    Attempt to reload TrayRunner configuration
    
    Returns:
        Tuple of (success, message)
    """
    # Find trayrunner executable
    exe = shutil.which("trayrunner")
    if not exe:
        return (False, "trayrunner not found in PATH")
    
    try:
        # Call trayrunner --reload
        result = subprocess.run(
            [exe, "--reload"],
            capture_output=True,
            text=True,
            timeout=10  # 10 second timeout
        )
        
        success = result.returncode == 0
        message = result.stdout.strip() or result.stderr.strip()
        
        if not message:
            message = "Reload OK" if success else "Reload failed"
        
        return (success, message)
        
    except subprocess.TimeoutExpired:
        return (False, "Reload command timed out")
    except FileNotFoundError:
        return (False, "trayrunner executable not found")
    except Exception as e:
        return (False, f"Failed to execute reload: {e}")


def is_trayrunner_running() -> bool:
    """
    Check if TrayRunner is currently running
    
    Returns:
        True if running, False otherwise
    """
    try:
        # Check if trayrunner process is running
        result = subprocess.run(
            ["pgrep", "-f", "python.*trayrunner"],
            capture_output=True,
            text=True
        )
        return result.returncode == 0 and result.stdout.strip()
    except Exception:
        return False


def get_trayrunner_status() -> Tuple[bool, str]:
    """
    Get TrayRunner status information
    
    Returns:
        Tuple of (is_running, status_message)
    """
    if not shutil.which("trayrunner"):
        return (False, "trayrunner command not found in PATH")
    
    try:
        # Try to get status using trayrunner status command
        result = subprocess.run(
            ["trayrunner", "status"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            return (True, result.stdout.strip())
        else:
            return (False, result.stderr.strip() or "TrayRunner not running")
            
    except subprocess.TimeoutExpired:
        return (False, "Status check timed out")
    except Exception as e:
        return (False, f"Status check failed: {e}")


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
        success, message = try_reload()
        
        self.last_reload_result = (success, message)
        self.last_reload_time = __import__('time').time()
        
        return success, message
    
    def get_last_reload_result(self) -> Tuple[bool, str]:
        """Get the result of the last reload attempt"""
        return self.last_reload_result or (False, "No reload attempted yet")
    
    def can_reload(self) -> bool:
        """Check if reload is possible (TrayRunner is running)"""
        return is_trayrunner_running()


# Global reload manager instance
reload_manager = ReloadManager()
